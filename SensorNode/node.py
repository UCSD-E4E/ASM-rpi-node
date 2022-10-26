import asyncio
import importlib
import logging
import os
import pkgutil
import platform
import socket
import time
import uuid
from typing import Awaitable, Callable, Dict, List, Set, Type
import subprocess
import yaml
from asm_protocol import codec

from SensorNode import sensor_nodes
import SensorNode


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
    def __getRevision(self) -> str:
        try:
            git_rev_parse = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
        except subprocess.CalledProcessError:
            git_rev_parse = ''
        try:
            git_diff_ret = subprocess.run(['git', 'diff', '--quiet']).returncode
        except Exception as e:
            git_diff_ret = 0
        if git_diff_ret != 0:
            git_rev_parse += ' dirty'
        return git_rev_parse

    def __init__(self, config_path: str):
        """Creates a new SensorNode object

        Args:
            path (str): Path to configuration file
        """
        self._log = logging.getLogger(self.__class__.__name__)
        self._log.info(f"Starting ASM Sensor Node v{SensorNode.__version__}, {self.__getRevision()}")
        if platform.system() not in ['posix', 'Linux']:
            raise RuntimeError('Not a Linux box!')

        if not os.path.exists(config_path):
            raise RuntimeError(f'Failed to open {config_path}')

        self._log.info("Loading configuration")
        with open(config_path, 'r') as file_stream:
            self._config_tree = yaml.safe_load(stream=file_stream)

        if self._config_tree is None:
            raise RuntimeError('Unable to read configuration file')
        for key in self.__config_keys:
            if key not in self._config_tree:
                raise RuntimeError(f'Key "{key}" not found in configuration '
                                   'file')
            self._log.info(f"Discovered {key}: {self._config_tree[key]}")

        try:
            self.uuid = uuid.UUID(self._config_tree['uuid'])
            self._log.info(f"I am {self.uuid}")
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
        self.port_number = int(self._config_tree['port'])
        self._log.info(f"Resolving endpoint as {self.data_endpoint}, UUID: {self.data_server_uuid}")

        if self.SENSOR_CLASS != "":
            if self.SENSOR_CLASS != self._config_tree['type']:
                raise RuntimeError('Invalid sensor class')

        self.codec = codec.Codec()

        self.heartbeat_period = int(self._config_tree['heartbeat_period_s'])

        self.__packetSendQueue: asyncio.Queue[codec.binaryPacket] = \
            asyncio.Queue()

        self._packet_handlers: Dict[Type[codec.binaryPacket],
                                    List[Callable[[codec.binaryPacket],
                                                 Awaitable[None]]]] = {}
        self._log.info("Codecs initialized")

        self.running: bool = True

    async def sendPacket(self, packet: codec.binaryPacket) -> None:
        try:
            await self.__packetSendQueue.put(packet)
            self._log.info(f"Queued Packet {packet}")
        except Exception:
            print("Failed to queue packet")
            self._log.exception("Failed to queue packet!")

    def registerPacketHandler(self, packetClass: Type[codec.binaryPacket],
                              callback: Callable[[codec.binaryPacket],
                                                 Awaitable[None]]) -> None:
        if packetClass not in self._packet_handlers:
            self._packet_handlers[packetClass] = [callback]
        else:
            self._packet_handlers[packetClass].append(callback)
        self._log.info(f"Registered {callback} for {packetClass}")

    async def sendHeartbeat(self) -> None:
        while True:
            heartbeat = codec.E4E_Heartbeat(self.uuid, self.uuid)
            await self.sendPacket(heartbeat)
            await asyncio.sleep(self.heartbeat_period)

    async def __sender(self):
        while True:
            try:
                packet_to_send = self.__packetSendQueue.get_nowait()
                self._log.info(f'Sending Packet {packet_to_send}')
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
                self._log.info(f'Received packet {packet}')
                if type(packet) in self._packet_handlers:
                    for handler in self._packet_handlers[type(packet)]:
                        await handler(packet)

    async def setup(self):
        pass

    def run(self):
        asyncio.run(self.__do_networking())
        self._log.info("Tasks completed")
        print('tasks done')

    async def __do_networking(self):
        while True:
            try:
                self.reader, self.writer = await asyncio.open_connection(self.data_endpoint, self.port_number)
                break
            except:
                continue
        heartbeat = asyncio.create_task(self.sendHeartbeat())
        receiver = asyncio.create_task(self.__receiver())
        sender = asyncio.create_task(self.__sender())
        self._log.info("Networking tasks created")
        setup = asyncio.create_task(self.setup())
        await asyncio.wait({receiver, sender, heartbeat, setup})


def __all_subclasses(cls: Type[object]) -> Set[Type[object]]:
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in __all_subclasses(c)]
    )


def iter_namespaces(ns_pkg):
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


def load_plugins():
    logger = logging.getLogger("NodeCreator")
    for _, name, _ in iter_namespaces(sensor_nodes):
        try:
            importlib.import_module(name)
        except:
            logger.error(f"Failed to import {name}")


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
    logger = logging.getLogger("NodeCreator")
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
        logger.info(f"Discovered {key}: {config_tree[key]}")

    load_plugins()

    sensor_node_classes = __all_subclasses(SensorNodeBase)
    sensor_node_table: Dict[str, Type[SensorNodeBase]] = {
        cls.SENSOR_CLASS: cls for cls in sensor_node_classes
        if issubclass(cls, SensorNodeBase)}

    if config_tree['type'] not in sensor_node_table:
        raise RuntimeError(f'Unknown sensor type {config_tree["type"]}')

    return sensor_node_table[config_tree['type']](configPath)
