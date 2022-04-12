import asyncio
import datetime as dt
import logging
import os
import shutil
import sys
from typing import Dict, Optional, Tuple, Type, Union

from asm_protocol import codec
from SensorNode import node
import ASM_utils.ffmpeg.audio as audio
import ASM_utils.ffmpeg.ffmpeg as ffmpeg
import ASM_utils.ffmpeg.rtp as rtp
import schema
try:
    import gpiozero
except ImportError:
    logging.exception("PWM LED will not function!")



class OnBoxSensorNode(node.SensorNodeBase):
    SENSOR_CLASS = 'ASM_NestingBox'

    NESTING_BOX_SCHEMA = schema.Schema({
        'video_endpoint': str,
        'illumination_on': str,
        'illumination_off': str,
        'illumination_level': schema.Or(int, float),
        'illumination_pin': int,
        'audio_endpoint': str,
        'audio_channels': int,
        'audio_samplerate': int,
        'audio_encoding': str
    })

    def __init__(self, config_path: str):
        super().__init__(config_path=config_path)
        if 'ASM_NESTING_BOX' not in self._config_tree:
            raise RuntimeError('No Nesting Box settings found')
        sensor_params = self._config_tree['ASM_NESTING_BOX']
        self.NESTING_BOX_SCHEMA.validate(sensor_params)
        self.camera_endpoint = sensor_params['video_endpoint']
        assert(isinstance(self.camera_endpoint, str))
        if self.camera_endpoint.startswith('/') and not os.path.exists(self.camera_endpoint):
            raise RuntimeError(f"Unable to find endpoint {self.camera_endpoint}")
        if shutil.which('ffmpeg') is None:
            raise RuntimeError('Unable to find ffmpeg in PATH!')

        self.__audio_source = audio.HWAudioSource(sensor_params['audio_endpoint'],
                                            num_channels=sensor_params['audio_channels'],
                                            sample_rate=sensor_params['audio_samplerate'])
        self.__audio_sink = rtp.RTPAudioStream(hostname=self.data_endpoint)
        self.__audio_sink.configure_audio(codec=sensor_params['audio_encoding'])

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
        command = codec.E4E_START_RTP_CMD(self.uuid, self.data_server_uuid, 2)
        await self.sendPacket(command)
        return await super().setup()

    async def onRTPCommandResponse(self, packet: codec.binaryPacket):
        assert(isinstance(packet, codec.E4E_START_RTP_RSP))
        if packet.streamID == 1:
            endpoint_port = packet.port
            cmd = (f'ffmpeg -f video4linux2 -input_format h264 -i {self.camera_endpoint}'
                f' -vcodec copy -f mpegts tcp://{self.data_endpoint}:{endpoint_port}')
            proc_out = asyncio.subprocess.PIPE
            proc_err = asyncio.subprocess.PIPE
            self._log.info(f'Starting ffmpeg with command: {cmd}')
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
            self.__audio_sink.set_port(packet.port)
            ffmpeg_config = ffmpeg.FFMPEGInstance(input_obj=self.__audio_source, output_obj=self.__audio_sink)
            cmd = ' '.join(ffmpeg_config.get_command())
            proc_out = asyncio.subprocess.PIPE
            proc_err = asyncio.subprocess.PIPE
            self._log.info(f'Starting ffmpeg with command: {cmd}')
            proc = await asyncio.create_subprocess_shell(cmd, stdout=proc_out, stderr=proc_err)

            retval = await proc.wait()
            if retval != 0:
                self._log.warning("ffmpeg shut down with error code %d", retval)
                self._log.info("ffmpeg stderr: %s", (await proc.stderr.read()).decode())
                self._log.info("ffmpeg stdout: %s", (await proc.stdout.read()).decode())
            else:
                self._log.info("ffmpeg returned with code %d", retval)
            if self.running:
                restart_cmd = codec.E4E_START_RTP_CMD(self.uuid, self.data_server_uuid, 1)
                await self.sendPacket(restart_cmd)

