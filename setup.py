from distutils.core import setup
import SensorNode

setup(
    name='SensorNode',
    version=SensorNode.__version__,
    description='Sensor Node',
    author='UC San Diego Engineers for Exploration',
    author_email='e4e@eng.ucsd.edu',
    packages=['SensorNode'],
    scripts=['runSensorNode.py'],
    install_requires=[
        "PyYaml"
    ]
)
