from SensorNode import sensor_nodes
import os
import platform
import socket
import uuid
from typing import Type, Set, Dict

import yaml
from asm_protocol import codec
import importlib
import pkgutil
import time
import queue
import select
import threading

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

        self.__packetSendQueue = queue.Queue()

    def sendPacket(self, packet: codec.binaryPacket):
        self.__packetSendQueue.put(packet)

    def registerPacketHandler(self, packetClass: Type[codec.binaryPacket]):
        pass

    def sendHeartbeatThread(self):
        heartbeat = codec.E4E_Heartbeat(self.__uuid, uuid.UUID('eff538d8-0ddb-11ec-80d8-5f5c814885d2'))
        while True:
            self.sendPacket(heartbeat)
            print("Sending heartbeat")
            time.sleep(self.heartbeat_period)

    def run(self):
        __heartbeat_thread = threading.Thread(target=self.sendHeartbeatThread)
        __heartbeat_thread.start()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as data_socket:
            print(f'Connecting to {self.data_endpoint}:{self.port_number}')
            data_socket.connect((self.data_endpoint, self.port_number))
            data_socket.setblocking(False)
            while self.runState:
                try:
                    packets_to_send = []
                    if not self.__packetSendQueue.empty():
                        packets_to_send.append(self.__packetSendQueue.get_nowait())
                        bytes_to_send = self.codec.encode(packets_to_send)
                        data_socket.sendall(bytes_to_send)
                except Exception as e:
                    print(e)
                    self.runState = False
                    raise e

                try:
                    data = data_socket.recv(65536)
                    self.codec.decode(data)
                except BlockingIOError:
                    pass
                except Exception as e:
                    print(e)
                    self.runState = False
                    raise e


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
        cls.SENSOR_CLASS: cls for cls in sensor_node_classes}

    if config_tree['type'] not in sensor_node_table:
        raise RuntimeError(f'Unknown sensor type {config_tree["type"]}')

    return sensor_node_table[config_tree['type']](configPath)
