import asyncio
from SensorNode import node
from asm_protocol import codec


class OnBoxSensorNode(node.SensorNodeBase):
    SENSOR_CLASS = 'ASM_NestingBox'

    NESTING_BOX_KEYS = {
        'video_endpoint': str
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

    async def setup(self):
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
