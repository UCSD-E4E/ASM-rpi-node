import asyncio
from dataclasses import dataclass
import datetime as dt
import os
from typing import Dict, List, Tuple, Type, Union

import schema
from asm_protocol import codec
from SensorNode import node

MOTOR_HAT_ENABLED = False
if os.path.exists('/sys/firmware/devicetree/base/model'):
    with open('/sys/firmware/devicetree/base/model', 'r') as model:
        pi_name = model.read()
        if pi_name.find('Raspberry Pi') != -1:
            MOTOR_HAT_ENABLED = True
            from RaspiMotorHat.Raspi_MotorHAT import \
                Raspi_MotorHAT as Raspi_MotorHAT

class AnimalFlipper(node.SensorNodeBase):
    SENSOR_CLASS = 'ASM_AnimalFlipper'

    KEYS: Dict[str, Union[Type, Tuple[Type, Type]]] = {
        'motor': int,
        'home_direction': int,
        'motor_steps': int,
        'motor_speed': int,
        'data_file': str
    }
    SCHEMA = schema.Schema(
        {
            'motor': schema.Or(1, 2),
            'home_direction': int,
            'motor_steps': int,
            'motor_speed': schema.Or(int, float),
            'home_direction': schema.Or(1, 2),
            'data_file': str,
            'loiter_time_s': schema.Or(int, float),
            'out_threshold_steps': int,
            'out_frame_steps': int,
            'safe_steps': int,
            'in_frame_steps': int,
            'in_threshold_steps': int
        }
    )

    IN_FRAME = 1
    PARTIAL_FRAME = 2
    OUT_FRAME = 3

    @dataclass
    class MotionPhase:
        steps: int
        direction: int
        label: int
        loiter: float

    def __init__(self, config_path: str = None):
        super().__init__(config_path=config_path)
        if self.SENSOR_CLASS not in self._config_tree:
            raise RuntimeError("No Aminal Flipper settings found")
        
        flipper_params = self._config_tree[self.SENSOR_CLASS]
        self.SCHEMA.validate(flipper_params)
        if MOTOR_HAT_ENABLED:
            self.motor_hat = Raspi_MotorHAT(0x6F)
            self.stepper = self.motor_hat.getStepper(flipper_params['motor_steps'], flipper_params['motor'])
            self.stepper.setSpeed(flipper_params['motor_speed'])
        else:
            self.__stepper_speed = 1 / flipper_params['motor_steps'] / flipper_params['motor_speed'] * 60.
            self._log.warn("Motor Hat not enabled!")

        self.home_distance = flipper_params['motor_steps']
        self.home_direction = flipper_params['home_direction']
        if self.home_direction == 1:
            self.in_direction = 1
            self.out_direction = 2
        else:
            self.in_direction = 2
            self.out_direction = 1

        self.__phases: List[AnimalFlipper.MotionPhase] = []
        self.__phases.append(AnimalFlipper.MotionPhase(
            steps=flipper_params['out_threshold_steps'],
            direction=self.out_direction,
            label=self.IN_FRAME,
            loiter=0
        ))
        self.__phases.append(AnimalFlipper.MotionPhase(
            steps=flipper_params['out_frame_steps'] - flipper_params['out_threshold_steps'],
            direction=self.out_direction,
            label=self.PARTIAL_FRAME,
            loiter=0
        ))
        self.__phases.append(AnimalFlipper.MotionPhase(
            steps=flipper_params['safe_steps'] - flipper_params['out_frame_steps'],
            direction=self.out_direction,
            label=self.OUT_FRAME,
            loiter=flipper_params['loiter_time_s']
        ))
        self.__phases.append(AnimalFlipper.MotionPhase(
            steps=flipper_params['safe_steps'] - flipper_params['in_frame_steps'],
            direction=self.in_direction,
            label=self.OUT_FRAME,
            loiter=0
        ))
        self.__phases.append(AnimalFlipper.MotionPhase(
            steps=flipper_params['in_frame_steps'] - flipper_params['in_threshold_steps'],
            direction=self.in_direction,
            label=self.PARTIAL_FRAME,
            loiter=0
        ))
        self.__phases.append(AnimalFlipper.MotionPhase(
            steps=flipper_params['in_threshold_steps'] + int(flipper_params['motor_steps'] / 4),
            direction=self.in_direction,
            label=self.IN_FRAME,
            loiter=flipper_params['loiter_time_s']
        ))
        
        if MOTOR_HAT_ENABLED:
            self.step_mode = Raspi_MotorHAT.MICROSTEP

        self.data_file = flipper_params['data_file']

    async def writeLabel(self, label: int):
        now = dt.datetime.utcnow()
        self._log.info(f'Recording label {label}')

        with open(self.data_file, 'a') as data_file:
            data_file.write(f'{now.isoformat()}: {label}\n')
        
        packet = codec.E4E_Data_Labels(
            label=label, 
            sourceUUID=self.uuid,
            destUUID=self.data_server_uuid,
            timestamp=now)
        
        await self.sendPacket(packet)

    async def flipTask(self):
        self._log.info("Slewing home")
        if MOTOR_HAT_ENABLED:
            self.stepper.step(self.home_distance, self.home_direction, self.step_mode)
        else:
            stepper_location = 0
            await asyncio.sleep(self.home_distance * self.__stepper_speed)
        self._log.info("Home")
        while self.running:
            for i, phase in enumerate(self.__phases):
                self._log.info(f'Doing phase {i}')
                await self.writeLabel(phase.label)
                if MOTOR_HAT_ENABLED:
                    self.stepper.step(phase.steps, phase.direction, self.step_mode)
                else:
                    self._log.info(f'Moving {phase.steps} in direction {phase.direction}')
                    await asyncio.sleep(phase.steps * self.__stepper_speed)
                    if phase.direction == 1:
                        stepper_location -= phase.steps
                    else:
                        stepper_location += phase.steps
                    if stepper_location < 0:
                        stepper_location = 0
                    self._log.info(f'Stepper now at {stepper_location}')
                await asyncio.sleep(phase.loiter)
            self._log.info('Home again')
                

    async def setup(self):
        asyncio.create_task(self.flipTask())
        return await super().setup()
