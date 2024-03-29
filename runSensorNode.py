#!/usr/bin/python
import os
import appdirs
import logging
import logging.handlers
import pathlib
import time

from SensorNode.node import createSensorNode


def main():
    if os.getuid() == 0:
        log_dest = os.path.join('var', 'log', 'asm_sensor_node.log')
    else:
        log_dir = appdirs.user_log_dir('ASMSensorNode')
        pathlib.Path(log_dir).mkdir(parents=True, exist_ok=True)
        log_dest = os.path.join(log_dir, 'asm_sensor_node.log')

    print(f"Logging to {log_dest}")
    root_logger = logging.getLogger()
    # Log to root to begin
    root_logger.setLevel(logging.DEBUG)

    log_file_handler = logging.handlers.RotatingFileHandler(log_dest, maxBytes=5*1024*1024, backupCount=5)
    log_file_handler.setLevel(logging.DEBUG)

    root_formatter = logging.Formatter('%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    log_file_handler.setFormatter(root_formatter)
    root_logger.addHandler(log_file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARN)

    error_formatter = logging.Formatter('%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    console_handler.setFormatter(error_formatter)
    root_logger.addHandler(console_handler)
    logging.Formatter.converter = time.gmtime

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