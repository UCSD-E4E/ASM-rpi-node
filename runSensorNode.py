#!/usr/bin/python
from SensorNode.node import runSensorNode

if __name__ == '__main__':
    sensor_node = runSensorNode('test_config.yaml')
    sensor_node.run()
