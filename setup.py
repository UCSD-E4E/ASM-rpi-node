from setuptools import setup, find_packages
import SensorNode
import os

default_requires = [
        "PyYaml",
        'asm_protocol',
        'bandit',
        'mypy',
        'RaspiMotorHat @ git+https://github.com/UCSD-E4E/Raspi-MotorHat@turnOffMotor',
        'appdirs',
        'schema',
        'AsmCommon',
]

pi_requires = [
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
    ]
)
