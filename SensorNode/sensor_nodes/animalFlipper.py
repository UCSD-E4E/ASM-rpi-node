import asyncio
import datetime as dt
from typing import Dict, Tuple, Type, Union

from asm_protocol import codec
from SensorNode import node

class AnimalFlipper(node.SensorNodeBase):
    SENSOR_CLASS = 'ASM_AnimalFlipper'

    KEYS: Dict[str, Union[Type, Tuple[Type, Type]]] = {
        'motor': int,
        'home_direction': int,
        'in_time_s': (int, float),
        'out_time_s': (int, float)
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
        