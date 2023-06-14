#!/usr/bin/python
import logging
import logging.handlers
import os
import pathlib
import time

import appdirs
from ASM_utils.logging import configure_logging

from SensorNode.node import createSensorNode


def main():
    if os.getuid() == 0:
        log_dest = os.path.join('var', 'log', 'asm_sensor_node.log')
    else:
        log_dir = appdirs.user_log_dir('ASMSensorNode')
        pathlib.Path(log_dir).mkdir(parents=True, exist_ok=True)
        log_dest = os.path.join(log_dir, 'asm_sensor_node.log')

    print(f"Logging to {log_dest}")
    configure_logging()
    root_logger = logging.getLogger()

    if os.path.isfile('asm_config.yaml'):
        config_file = 'asm_config.yaml'
    elif os.path.isfile('/usr/local/etc/asm_config.yaml'):
        config_file = '/usr/local/etc/asm_config.yaml'
    elif os.path.isfile('/boot/asm_config.yaml'):
        config_file = '/boot/asm_config.yaml'
    else:
        raise RuntimeError("Config file not found")
    root_logger.info(f"Using config file {config_file}")
    print(f"Using config file {config_file}")

    try:
        sensor_node = createSensorNode(config_file)
    except Exception as e:
        root_logger.exception(f"Failed to create node: {e}")
        return

    try:
        sensor_node.run()
    except Exception as e:
        root_logger.exception(f"Failed to run node: {e}")
        
if __name__ == '__main__':
    main()