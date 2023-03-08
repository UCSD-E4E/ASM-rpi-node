"""Example setup file
"""
from pathlib import Path

from setuptools import find_packages, setup

import sensor_node

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

firmware_model = Path('/sys/firmware/devicetree/base/model')
if firmware_model.exists():
    with open(firmware_model, 'r', encoding='ascii') as model:
        pi_name = model.read()
        if pi_name.find('Raspberry Pi') != -1:
            default_requires.extend(pi_requires)

setup(
    name='SensorNode',
    version=sensor_node.__version__,
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
