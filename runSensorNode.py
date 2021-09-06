#!/usr/bin/python
from SensorNode.node import runSensorNode
import asyncio
import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    sensor_node = runSensorNode('test_config.yaml')
    asyncio.run(sensor_node.run(), debug=True)
