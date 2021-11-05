import asyncio
import importlib
import os
import pkgutil
import platform
import socket
import time
import uuid
from typing import Awaitable, Callable, Dict, List, Set, Type

import yaml
from asm_protocol import codec

from SensorNode import sensor_nodes


class SensorNodeBase:
    __config_keys = [
        'uuid',
        'type',
        'data_server',
        'port',
        'heartbeat_period_s',
        'data_server_uuid'
    ]

    SENSOR_CLASS = ""

    def __init__(self, config_path: str = None):
        """Creates a new SensorNode object

        Args:
            path (str): Path to configuration file
        """
        self.runState = True
        if platform.system() not in ['posix', 'Linux']:
            raise RuntimeError('Not a Linux box!')
        if config_path is None:
            config_path = '/boot/asm_config.yaml'
        if not os.path.exists(config_path):
            raise RuntimeError(f'Failed to open {config_path}')
        with open(config_path, 'r') as file_stream:
            self._config_tree = yaml.safe_load(stream=file_stream)
        if self._config_tree is None:
            raise RuntimeError('Unable to read configuration file')
        for key in self.__config_keys:
            if key not in self._config_tree:
                raise RuntimeError(f'Key "{key}" not found in configuration '
                                   'file')
        try:
            self.uuid = uuid.UUID(self._config_tree['uuid'])
        except Exception:
            raise RuntimeError("Unable to create uuid from "
                               f"{self._config_tree['uuid']}")
        endpoint = self._config_tree['data_server']
        self.data_endpoint = None
        while self.data_endpoint is None:
            try:
                self.data_endpoint = socket.gethostbyname(endpoint)
            except:
                time.sleep(1)
        uuid_str = self._config_tree['data_server_uuid']
        self.data_server_uuid = uuid.UUID(uuid_str)

        if self.SENSOR_CLASS != "":
            if self.SENSOR_CLASS != self._config_tree['type']:
                raise RuntimeError('Invalid sensor class')

        self.port_number = int(self._config_tree['port'])
        self.codec = codec.Codec()

        self.heartbeat_period = int(self._config_tree['heartbeat_period_s'])

        self.__packetSendQueue: asyncio.Queue[codec.binaryPacket] = \
            asyncio.Queue()

        self._packet_handlers: Dict[Type[codec.binaryPacket],
                                    List[Callable[[codec.binaryPacket],
                                                  Awaitable[None]]]] = {}
        self.running = True

    async def sendPacket(self, packet: codec.binaryPacket) -> None:
        try:
            await self.__packetSendQueue.put(packet)
            print('Queued packet')
            print(self.__packetSendQueue.qsize())
        except Exception:
            print("Failed to queue packet")

    def registerPacketHandler(self, packetClass: Type[codec.binaryPacket],
                              callback: Callable[[codec.binaryPacket],
                                                 Awaitable[None]]) -> None:
        if packetClass not in self._packet_handlers:
            self._packet_handlers[packetClass] = [callback]
        else:
            self._packet_handlers[packetClass].append(callback)

    async def sendHeartbeat(self) -> None:
        while True:
            heartbeat = codec.E4E_Heartbeat(self.uuid, self.uuid)
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
                        await handler(packet)

    async def setup(self):
        pass

    def run(self):
        asyncio.run(self.__do_networking())
        print('tasks done')

    async def __do_networking(self):
        self.reader, self.writer = await \
            asyncio.open_connection(self.data_endpoint, self.port_number)
        heartbeat = asyncio.create_task(self.sendHeartbeat())
        receiver = asyncio.create_task(self.__receiver())
        sender = asyncio.create_task(self.__sender())
        setup = asyncio.create_task(self.setup())
        await asyncio.wait({receiver, sender, heartbeat, setup})


def __all_subclasses(cls: Type[object]) -> Set[Type[object]]:
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in __all_subclasses(c)]
    )


def iter_namespaces(ns_pkg):
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


def load_plugins():
    for _, name, _ in iter_namespaces(sensor_nodes):
        try:
            importlib.import_module(name)
        except:
            print(f"Failed to import {name}")


def createSensorNode(configPath: str) -> SensorNodeBase:
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
