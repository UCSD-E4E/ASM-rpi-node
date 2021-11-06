from setuptools import setup, find_packages
import SensorNode

setup(
    name='SensorNode',
    version=SensorNode.__version__,
    description='Sensor Node',
    author='UC San Diego Engineers for Exploration',
    author_email='e4e@eng.ucsd.edu',
    packages=find_packages(),
    scripts=['runSensorNode.py'],
    install_requires=[
        "PyYaml",
        'asm_protocol',
        'bandit',
        'mypy'
    ]
)
