#!/usr/bin/python
import os

from SensorNode.node import createSensorNode

if __name__ == '__main__':
    if os.path.isfile('/boot/asm_config.yaml'):
        sensor_node = createSensorNode('/boot/asm_config.yaml')
    elif os.path.isfile('/usr/local/etc/asm_config.yaml'):
        sensor_node = createSensorNode('/usr/local/etc/asm_config.yaml')
    else:
        sensor_node = createSensorNode('asm_config.yaml')
    sensor_node.run()
