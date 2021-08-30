import os
import platform
import socket
import uuid

import yaml


class SensorNode:
    config_keys = [
        'uuid',
        'type',
        'data_server'
    ]

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
        ip_address = socket.gethostbyname(config_tree['data_server'])
        print(ip_address)
