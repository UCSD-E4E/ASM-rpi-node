import asyncio
import datetime as dt
import sys
from typing import Dict, Optional, Tuple, Type, Union

from asm_protocol import codec
from SensorNode import node

try:
    import gpiozero
except ImportError:
    print("Warning: PWM LED will not function!")


class OnBoxSensorNode(node.SensorNodeBase):
    SENSOR_CLASS = 'ASM_NestingBox'

    NESTING_BOX_KEYS: Dict[str, Union[Type, Tuple[Type, Type]]] = {
        'video_endpoint': str,
        'illumination_on': str,
        'illumination_off': str,
        'illumination_level': (int, float),
        'illumination_pin': str
    }

    def __init__(self, config_path: str):
        super().__init__(config_path=config_path)
        if 'ASM_NESTING_BOX' not in self._config_tree:
            raise RuntimeError('No Nesting Box settings found')
        sensor_params = self._config_tree['ASM_NESTING_BOX']
        for key, key_type in self.NESTING_BOX_KEYS.items():
            if key not in sensor_params:
                raise RuntimeError(f'Key {key} not found in Nestimg Box '
                                   'settings')
            if not isinstance(sensor_params[key], key_type):
                raise RuntimeError(f'Expecting {key_type} for ASM_NESTING_BOX.'
                                   f'{key}, got {type(sensor_params[key])} '
                                   'instead!')
        self.camera_endpoint = sensor_params['video_endpoint']
        assert(isinstance(self.camera_endpoint, str))

        self.__running = True

        self.registerPacketHandler(codec.E4E_START_RTP_RSP,
                                   self.onRTPCommandResponse)

        self.led: Optional[gpiozero.PWMLED] = None
        if 'gpiozero' in sys.modules:
            pin = sensor_params['illumination_pin']
            self.led = gpiozero.PWMLED(pin)
            self.led_on: dt.time = dt.time.fromisoformat(
                sensor_params['illumination_on'])
            self.led_off: dt.time = dt.time.fromisoformat(
                sensor_params['illumination_off'])
            self.led_value: float = sensor_params['illumination_level'] / 100

    async def turnLEDOn(self):
        while self.led:
            targetTime = dt.datetime.combine(dt.date.today(), self.led_on)
            now = dt.datetime.now()
            if targetTime < now:
                targetTime += dt.timedelta(days=1)

            sleep_time = (targetTime - now).total_seconds()
            await asyncio.sleep(sleep_time)
            self.led.value = self.led_value

    async def turnLEDOff(self):
        while self.led:
            targetTime = dt.datetime.combine(dt.date.today(), self.led_off)
            now = dt.datetime.now()
            if targetTime < now:
                targetTime += dt.timedelta(days=1)

            sleep_time = (targetTime - now).total_seconds()
            await asyncio.sleep(sleep_time)
            self.led.value = 0

    async def setup(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.turnLEDOff())
        loop.create_task(self.turnLEDOn())
        command = codec.E4E_START_RTP_CMD(self.uuid, self.data_server_uuid)
        await self.sendPacket(command)
        return await super().setup()

    async def onRTPCommandResponse(self, packet: codec.binaryPacket):
        assert(isinstance(packet, codec.E4E_START_RTP_RSP))
        endpoint_port = packet.port
        cmd = (f'ffmpeg -i {self.camera_endpoint} -acodec libmp3lame -ar 11025'
               f' -f mpegts tcp://{self.data_endpoint}:{endpoint_port}')
        proc_out = asyncio.subprocess.PIPE
        proc_err = asyncio.subprocess.PIPE
        proc = await asyncio.create_subprocess_shell(cmd,
                                                     stdout=proc_out,
                                                     stderr=proc_err)
        await proc.wait()
        if self.__running:
            restart_cmd = codec.E4E_START_RTP_CMD(self.uuid,
                                                  self.data_server_uuid)
            await self.sendPacket(restart_cmd)
