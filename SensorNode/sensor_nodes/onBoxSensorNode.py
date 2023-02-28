import asyncio
import datetime as dt
import logging
import os
import pathlib
import shutil
import sys
from typing import Dict, Optional, Tuple, Type, Union

import appdirs
from asm_protocol import codec
from SensorNode import node

try:
    import gpiozero
except ImportError:
    logging.exception("PWM LED will not function!")



class OnBoxSensorNode(node.SensorNodeBase):
    SENSOR_CLASS = 'ASM_NestingBox'

    NESTING_BOX_KEYS: Dict[str, Union[Type, Tuple[Type, Type]]] = {
        'video_endpoint': str,
        'illumination_on': str,
        'illumination_off': str,
        'illumination_level': (int, float),
        'illumination_pin': int
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
            self._log.info(f'Discovered {key}: {sensor_params[key]}')
        self.camera_endpoint = sensor_params['video_endpoint']
        assert(isinstance(self.camera_endpoint, str))
        if self.camera_endpoint.startswith('/') and not os.path.exists(self.camera_endpoint):
            raise RuntimeError(f"Unable to find endpoint {self.camera_endpoint}")
        if shutil.which('ffmpeg') is None:
            raise RuntimeError('Unable to find ffmpeg in PATH!')

        if os.getuid() == 0:
            self.ff_log_dir = pathlib.Path('var', 'log', 'ffmpeg_logs').absolute()
        else:
            # absolute() not necessary because of ASMSensorNode dir
            self.ff_log_dir = pathlib.Path(appdirs.user_log_dir('ASMSensorNode'), 'ffmpeg_logs')

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
        else:
            self._log.warning("LED will not function")

    async def LEDTask(self):
        while self.led is not None:
            while self.running:
                now = dt.datetime.now()
                on_time = dt.datetime.combine(dt.date.today(), self.led_on)
                off_time = dt.datetime.combine(dt.date.today(), self.led_off)
                ordered_time = {on_time: self.led_value, off_time: 0}
                current_state = ordered_time[max(on_time, off_time)]
                for threshold_time in sorted(ordered_time.keys()):
                    if now > threshold_time:
                        current_state = ordered_time[threshold_time]
                self.led.value = current_state
                await asyncio.sleep(30)

    async def setup(self):
        asyncio.create_task(self.LEDTask())
        command = codec.E4E_START_RTP_CMD(self.uuid, self.data_server_uuid, 1)
        await self.sendPacket(command)
        return await super().setup()

    async def onRTPCommandResponse(self, packet: codec.binaryPacket):
        assert(isinstance(packet, codec.E4E_START_RTP_RSP))
        if packet.streamID == 1:
            endpoint_port = packet.port

            ff_stats_path = pathlib.Path(self.ff_log_dir, "ffstats.log")
            ff_info_path = pathlib.Path(self.ff_log_dir, "ffinfo.log")
            split_script = "-m ASM_utils.ffmpeg.split_log"

            cmd = (f'ffmpeg -f video4linux2 -input_format h264 -i {self.camera_endpoint}'
                f' -vcodec copy -f mpegts tcp://{self.data_endpoint}:{endpoint_port} '
                f' 2>&1 | {sys.executable} {split_script} {ff_stats_path} {ff_info_path}')
            
            if not self.data_endpoint2 is None:
                cmd = (f'ffmpeg -f video4linux2 -input_format h264 -i {self.camera_endpoint}'
                f' -vcodec copy -f mpegts tcp://{self.data_endpoint}:{10010} '
                f' -vcodec copy -f mpegts tcp://{self.data_endpoint2}:{self.port2_number}'
                f' 2>&1 | {sys.executable} {split_script} {ff_stats_path} {ff_info_path}')
                print(f"streaming with :{cmd}")
            proc_out = asyncio.subprocess.PIPE
            proc_err = asyncio.subprocess.PIPE
            self._log.info(f'Starting ffmpeg with command: {cmd}')
            self._log.info(f"FFmpeg logging to: {self.ff_log_dir}")
            proc = await asyncio.create_subprocess_shell(cmd,
                                                        stdout=proc_out,
                                                        stderr=proc_err)
            retval = await proc.wait()
            if retval != 0:
                self._log.warning("ffmpeg shut down with error code %d", retval)
                self._log.info("ffmpeg stderr: %s", (await proc.stderr.read()).decode())
                self._log.info("ffmpeg stdout: %s", (await proc.stdout.read()).decode())
            else:
                self._log.info("ffmpeg returned with code %d", retval)
            if self.running:
                restart_cmd = codec.E4E_START_RTP_CMD(self.uuid,
                                                    self.data_server_uuid, 1)
                await self.sendPacket(restart_cmd)
        elif packet.streamID == 2:
            # set up audio streaming
            pass
