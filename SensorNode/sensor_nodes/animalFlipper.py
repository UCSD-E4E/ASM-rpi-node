import asyncio
import datetime as dt
import os
from typing import Dict, Tuple, Type, Union

from asm_protocol import codec
from SensorNode import node
from RaspiMotorHat.Raspi_MotorHAT import Raspi_MotorHAT as Raspi_MotorHAT

class AnimalFlipper(node.SensorNodeBase):
    SENSOR_CLASS = 'ASM_AnimalFlipper'

    KEYS: Dict[str, Union[Type, Tuple[Type, Type]]] = {
        'motor': int,
        'home_direction': int,
        'in_time_s': (int, float),
        'in_steps': int,
        'out_time_s': (int, float),
        'out_steps': int,
        'motor_steps': int,
        'motor_speed': int,
        'data_file': str
    }

    def __init__(self, config_path: str = None):
        super().__init__(config_path=config_path)
        if self.SENSOR_CLASS not in self._config_tree:
            raise RuntimeError("No Aminal Flipper settings found")
        
        flipper_params = self._config_tree[self.SENSOR_CLASS]
        for key, key_type in self.KEYS.items():
            if key not in flipper_params:
                raise RuntimeError(f'Key {key} not found in Flipper '
                                   'settings')
            if not isinstance(flipper_params[key], key_type):
                raise RuntimeError(f'Expecting {key_type} for {self.SENSOR_CLASS}.'
                                   f'{key}, got {type(flipper_params[key])} '
                                   'instead!')
        
        self.motor_hat = Raspi_MotorHAT(0x6F)
        self.stepper = self.motor_hat.getStepper(flipper_params['motor_steps'], flipper_params['motor'])
        self.home_distance = flipper_params['motor_steps']
        self.stepper.setSpeed(flipper_params['motor_speed'])

        self.in_time_s = flipper_params['in_time_s']
        self.out_time_s = flipper_params['out_time_s']
        self.in_steps = flipper_params['in_steps']
        self.out_steps = flipper_params['out_steps']
        self.home_direction = flipper_params['home_direction']
        if self.home_direction not in [1, 2]:
            raise RuntimeError(f'Invalid home direction: {self.home_direction}')
        if self.home_direction == 1:
            self.in_direction = 1
            self.out_direction = 2
        else:
            self.in_direction = 2
            self.out_direction = 1
        self.step_mode = Raspi_MotorHAT.MICROSTEP

        self.data_file = flipper_params['data_file']

    async def flipTask(self):
        self.stepper.step(self.home_distance, self.home_direction, self.step_mode)
        with open(self.data_file, 'a') as data_file:
            while self.running:
                self.stepper.step(self.out_steps, self.out_direction, self.step_mode)
                now = dt.datetime.utcnow().isoformat()
                data_file.write(f'{now}: out\n')
                data_file.flush()
                self.motor_hat.turnOffMotors()
                await asyncio.sleep(self.out_time_s)

                self.stepper.step(self.in_steps, self.in_direction, self.step_mode)
                now = dt.datetime.utcnow().isoformat()
                data_file.write(f'{now}: in\n')
                data_file.flush()
                self.motor_hat.turnOffMotors()
                await asyncio.sleep(self.in_time_s)

    async def setup(self):
        asyncio.create_task(self.flipTask())
        return await super().setup()        