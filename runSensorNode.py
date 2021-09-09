#!/usr/bin/python
import os

from SensorNode.node import runSensorNode

if __name__ == '__main__':
    if os.path.isfile('/boot/asm_config.yaml'):
        sensor_node = runSensorNode('/boot/asm_config.yaml')
    elif os.path.isfile('/usr/local/etc/asm_config.yaml'):
        sensor_node = runSensorNode('/usr/local/etc/asm_config.yaml')
    else:
        sensor_node = runSensorNode('asm_config.yaml')
    sensor_node.run()
