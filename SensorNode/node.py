import asyncio
import importlib
import os
import pkgutil
import platform
import socket
import uuid
from typing import Callable, Dict, List, Set, Type

import yaml
from asm_protocol import codec

from SensorNode import sensor_nodes


class SensorNodeBase:
    config_keys = [
        'uuid',
        'type',
        'data_server',
        'port',
        'heartbeat_period_s'
    ]

    SENSOR_CLASS = ""

    def __init__(self, path: str = None):
        """Creates a new SensorNode object

        Args:
            path (str): Path to configuration file
        """
        self.runState = True
        if platform.system() not in ['posix', 'Linux']:
            raise RuntimeError('Not a Linux box!')
        if path is None:
            path = '/boot/asm_config.yaml'
        if not os.path.exists(path):
            raise RuntimeError(f'Failed to open {path}')
        with open(path, 'r') as file_stream:
            config_tree = yaml.safe_load(stream=file_stream)
        if config_tree is None:
            raise RuntimeError('Unable to read configuration file')
        for key in self.config_keys:
            if key not in config_tree:
                raise RuntimeError(f'Key "{key}" not found in configuration '
                                   'file')
        try:
            self.__uuid = uuid.UUID(config_tree['uuid'])
        except Exception:
            raise RuntimeError("Unable to create uuid from "
                               f"{config_tree['uuid']}")
        self.data_endpoint = socket.gethostbyname(config_tree['data_server'])
        if self.SENSOR_CLASS != "":
            if self.SENSOR_CLASS != config_tree['type']:
                raise RuntimeError('Invalid sensor class')

        self.port_number = int(config_tree['port'])
        self.codec = codec.Codec()

        self.heartbeat_period = int(config_tree['heartbeat_period_s'])

        self.__packetSendQueue: asyncio.Queue[codec.binaryPacket] = \
            asyncio.Queue()

        self._packet_handlers: Dict[Type[codec.binaryPacket],
                                    List[Callable[[codec.binaryPacket],
                                                  None]]] = {}

    async def sendPacket(self, packet: codec.binaryPacket):
        try:
            await self.__packetSendQueue.put(packet)
            print('Queued packet')
            print(self.__packetSendQueue.qsize())
        except Exception:
            print("Failed to queue packet")

    def registerPacketHandler(self, packetClass: Type[codec.binaryPacket],
                              callback: Callable[[codec.binaryPacket], None]):
        if packetClass not in self._packet_handlers:
            self._packet_handlers[packetClass] = [callback]
        else:
            self._packet_handlers[packetClass].append(callback)

    async def sendHeartbeat(self):
        while True:
            heartbeat = codec.E4E_Heartbeat(self.__uuid, self.__uuid)
            await self.sendPacket(heartbeat)
            await asyncio.sleep(self.heartbeat_period)

    async def __sender(self):
        while True:
            try:
                packet_to_send = self.__packetSendQueue.get_nowait()
                bytes_to_send = self.codec.encode([packet_to_send])
                self.writer.write(bytes_to_send)
                await self.writer.drain()
            except asyncio.queues.QueueEmpty:
                await asyncio.sleep(0)
                continue

    async def __receiver(self):
        while True:
            bytes_received = await self.reader.read(65536)
            packets_received = self.codec.decode(bytes_received)
            for packet in packets_received:
                if type(packet) in self._packet_handlers:
                    for handler in self._packet_handlers[type(packet)]:
                        handler(packet)

    async def run(self):
        self.reader, self.writer = await \
            asyncio.open_connection(self.data_endpoint, self.port_number)
        heartbeat = asyncio.create_task(self.sendHeartbeat())
        receiver = asyncio.create_task(self.__receiver())
        sender = asyncio.create_task(self.__sender())
        await asyncio.wait({receiver, sender, heartbeat})
        print('tasks done')


def __all_subclasses(cls: Type[object]) -> Set[Type[object]]:
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in __all_subclasses(c)]
    )


def iter_namespaces(ns_pkg):
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


def load_plugins():
    for _, name, _ in iter_namespaces(sensor_nodes):
        importlib.import_module(name)


def runSensorNode(configPath: str) -> SensorNodeBase:
    """Instantiates the proper SensorNode class given the parameters in
    configPath

    Args:
        configPath (str): Configuration File

    Raises:
        RuntimeError: Raised if not a Linux machine, invalid configuration
        path, or invalid configuration file

    Returns:
        SensorNode: SensorNode instance
    """
    config_keys = [
        'uuid',
        'type',
        'data_server'
    ]
    if platform.system() not in ['posix', 'Linux']:
        raise RuntimeError('Not a Linux box!')
    if configPath is None:
        configPath = '/boot/asm_config.yaml'
    if not os.path.exists(configPath):
        raise RuntimeError(f'Failed to open {configPath}')
    with open(configPath, 'r') as file_stream:
        config_tree = yaml.safe_load(stream=file_stream)
    if config_tree is None:
        raise RuntimeError('Unable to read configuration file')
    for key in config_keys:
        if key not in config_tree:
            raise RuntimeError(f'Key "{key}" not found in configuration '
                               'file')

    load_plugins()

    sensor_node_classes = __all_subclasses(SensorNodeBase)
    sensor_node_table: Dict[str, Type[SensorNodeBase]] = {
        cls.SENSOR_CLASS: cls for cls in sensor_node_classes
        if issubclass(cls, SensorNodeBase)}

    if config_tree['type'] not in sensor_node_table:
        raise RuntimeError(f'Unknown sensor type {config_tree["type"]}')

    return sensor_node_table[config_tree['type']](configPath)
