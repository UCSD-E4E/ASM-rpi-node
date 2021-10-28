import asyncio
from SensorNode import node
from asm_protocol import codec


class RemoteSensorNode(node.SensorNodeBase):
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
        self.ip_camera_address = ip_camera_params['address']
        assert(isinstance(self.ip_camera_address, str))
        self.ip_camera_user = ip_camera_params['user']
        assert(isinstance(self.ip_camera_user, str))
        self.ip_camera_password = ip_camera_params['password']
        assert(isinstance(self.ip_camera_password, str))
        self.ip_camera_port = ip_camera_params['port']
        assert(isinstance(self.ip_camera_port, int))


        self.registerPacketHandler(codec.E4E_START_RTP_RSP,
                                   self.onRTPCommandResponse)

    async def setup(self):
        command = codec.E4E_START_RTP_CMD(self.uuid, self.data_server_uuid, 1)
        await self.sendPacket(command)
        return await super().setup()

    async def onRTPCommandResponse(self, packet: codec.binaryPacket):
        assert(isinstance(packet, codec.E4E_START_RTP_RSP))
        endpoint_port = packet.port
        cmd = (f'ffmpeg -f video4linux2 -input_format h264 -i rtsp://{self.ip_camera_user}:'
               f'{self.ip_camera_password}@{self.ip_camera_address}:'
               f'{self.ip_camera_port}/live.sdp -acodec libmp3lame -ar 11025 -vcodec copy '
               f'-f mpegts tcp://{self.data_endpoint}:{endpoint_port}')
        proc_out = asyncio.subprocess.PIPE
        proc_err = asyncio.subprocess.PIPE
        proc = await asyncio.create_subprocess_shell(cmd,
                                                     stdout=proc_out,
                                                     stderr=proc_err)
        await proc.wait()
        if self.running:
            restart_cmd = codec.E4E_START_RTP_CMD(self.uuid,
                                                  self.data_server_uuid, packet.streamID)
            await self.sendPacket(restart_cmd)
