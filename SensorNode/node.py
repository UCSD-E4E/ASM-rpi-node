import os
import platform
import socket
import uuid
from typing import Type, Set, Dict

import yaml
from SensorNode.codec import binaryPacket


class SensorNode:
    config_keys = [
        'uuid',
        'type',
        'data_server'
    ]

    SENSOR_CLASS = ""

    def __init__(self, path: str = None):
        """Creates a new SensorNode object

        Args:
            path (str): Path to configuration file
        """
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
        socket.gethostbyname(config_tree['data_server'])
        if self.SENSOR_CLASS != "":
            if self.SENSOR_CLASS != config_tree['type']:
                raise RuntimeError('Invalid sensor class')

    def sendPacket(self, packet: binaryPacket):
        pass

    def registerPacketHandler(self, packetClass: Type[binaryPacket]):
        pass

    def run(self):
        while True:
            pass


def __all_subclasses(cls: Type[object]) -> Set[Type[object]]:
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in __all_subclasses(c)]
    )


def runSensorNode(configPath: str) -> SensorNode:
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

    sensor_node_classes = __all_subclasses(SensorNode)
    sensor_node_table: Dict[str, Type[SensorNode]] = {
        cls.SENSOR_CLASS: cls for cls in sensor_node_classes}

    if config_tree['type'] not in sensor_node_table:
        raise RuntimeError(f'Unknown sensor type {config_tree["type"]}')

    return sensor_node_table[config_tree['type']](configPath)
