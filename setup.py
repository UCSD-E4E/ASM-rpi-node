"""Example setup file
"""
import os

from setuptools import find_packages, setup

import SensorNode

default_requires = [
        "PyYaml",
        'asm_protocol',
        'bandit',
        'mypy',
        'appdirs',
        'schema',
]

pi_requires = [
    'RaspiMotorHat @ git+https://github.com/UCSD-E4E/Raspi-MotorHat@turnOffMotor',
    'gpiozero',
    'rpi.gpio'
]

if os.path.exists('/sys/firmware/devicetree/base/model'):
    with open('/sys/firmware/devicetree/base/model', 'r') as model:
        pi_name = model.read()
        if pi_name.find('Raspberry Pi') != -1:
            default_requires.extend(pi_requires)

setup(
    name='SensorNode',
    version=SensorNode.__version__,
    description='Sensor Node',
    author='UC San Diego Engineers for Exploration',
    author_email='e4e@eng.ucsd.edu',
    packages=find_packages(),
    scripts=['runSensorNode.py'],
    install_requires=[
        default_requires
    ],
    extras_require={
        'dev': [
            'pytest',
            'coverage',
            'pylint',
            'wheel',
        ]
    },
)
