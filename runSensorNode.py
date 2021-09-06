#!/usr/bin/python
from SensorNode.node import runSensorNode
import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    sensor_node = runSensorNode('test_config.yaml')
    sensor_node.run()
