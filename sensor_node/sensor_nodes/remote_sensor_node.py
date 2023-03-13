'''Remote Sensor Node
'''
import asyncio
import os
import pathlib
import sys

import appdirs
from asm_protocol import codec
from sensor_node import node


class RemoteSensorNode(node.SensorNodeBase):
    """Remote Sensor Node

    Args:
        node (str): config_path

    Raises:
        RuntimeError: Key not found in config file
        RuntimeError: Invalid value type
        RuntimeError: IP Camera settings not found

    Returns:
        node.SensorNodeBase: Sensor Node
    """
    SENSOR_CLASS = 'IP_Camera'

    IP_CAMERA_KEYS = {
        'address': str,
        'user': str,
        'password': str,
        'port': int
    }

    def __init__(self, config_path: str):
        super().__init__(config_path=config_path)
        if 'IP_CAMERA' not in self._config_tree:
            raise RuntimeError('No IP Camera settings found')
        ip_camera_params = self._config_tree['IP_CAMERA']
        for key, key_type in self.IP_CAMERA_KEYS.items():
            if key not in ip_camera_params:
                raise RuntimeError(f'Key {key} not found in IP Camera '
                                   'settings')
            if not isinstance(ip_camera_params[key], key_type):
                raise RuntimeError(f'Expecting {key_type} for IP_CAMERA.{key},'
                                   f' got {type(ip_camera_params[key])} '
                                   'instead!')
            self._log.info('Discovered %s: %s', key, ip_camera_params[key])
        self.ip_camera_address = ip_camera_params['address']
        assert isinstance(self.ip_camera_address, str)
        self.ip_camera_user = ip_camera_params['user']
        assert isinstance(self.ip_camera_user, str)
        self.ip_camera_password = ip_camera_params['password']
        assert isinstance(self.ip_camera_password, str)
        self.ip_camera_port = ip_camera_params['port']
        assert isinstance(self.ip_camera_port, int)

        if os.getuid() == 0:
            self.ff_log_dir = pathlib.Path('var', 'log', 'ffmpeg_logs').absolute()
        else:
            # absolute() not necessary because of ASMSensorNode dir
            self.ff_log_dir = pathlib.Path(appdirs.user_log_dir('ASMSensorNode'), 'ffmpeg_logs')
        pathlib.Path(self.ff_log_dir).mkdir(parents=True, exist_ok=True)

        self.registerPacketHandler(codec.E4E_START_RTP_RSP,
                                   self.on_rtp_cmd_response)

    async def setup(self):
        command = codec.E4E_START_RTP_CMD(self.uuid, self.data_server_uuid, 1)
        await self.sendPacket(command)
        return await super().setup()

    async def on_rtp_cmd_response(self, packet: codec.binaryPacket):
        """On RTP Command response callback

        Args:
            packet (codec.binaryPacket): Binary packet
        """
        assert isinstance(packet, codec.E4E_START_RTP_RSP)
        endpoint_port = packet.port

        ff_stats_path = pathlib.Path(self.ff_log_dir, "ffstats.log")
        ff_info_path = pathlib.Path(self.ff_log_dir, "ffinfo.log")
        split_script = "-m ASM_utils.ffmpeg.split_log"

        cmd = (f'ffmpeg -i rtsp://{self.ip_camera_user}:'
               f'{self.ip_camera_password}@{self.ip_camera_address}:'
               f'{self.ip_camera_port}/live.sdp -acodec libmp3lame -ar 11025 -vcodec copy '
               f'-f mpegts tcp://{self.data_endpoint}:{endpoint_port}'
               f' 2>&1 | {sys.executable} {split_script} {ff_stats_path} {ff_info_path}'
               )
        proc_out = asyncio.subprocess.PIPE
        proc_err = asyncio.subprocess.PIPE
        self._log.info('Starting ffmpeg with command: %s', cmd)
        self._log.info("FFmpeg logging to: %s", self.ff_log_dir)
        proc = await asyncio.create_subprocess_shell(cmd,
                                                     stdout=proc_out,
                                                     stderr=proc_err)

        retval = await proc.wait()
        if retval != 0:
            self._log.warning("ffmpeg shut down with error code %d", retval)
            self._log.info("ffmpeg stderr: %s", (await proc.stderr.read()).decode())
            self._log.info("ffmpeg stdout: %s", (await proc.stdout.read()).decode())
        else:
            self._log.info("ffmpeg returned with error code %d", retval)
        if self.running:
            restart_cmd = codec.E4E_START_RTP_CMD(self.uuid,
                                                  self.data_server_uuid, packet.streamID)
            await self.sendPacket(restart_cmd)
