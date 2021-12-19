from typing import Dict, List, Optional
from SensorNode.utils.ffmpeg import MediaOutput

class RTPOutputStream(MediaOutput):
    def __init__(self, hostname:str, port:int, protocol:str = 'tcp', format:str = 'mpegts'):
        self.__protocol = protocol
        self.__hostname = hostname
        self.__port = port
        self.__audio_flags:Dict[str, str] = {}
        self.__video_flags:Dict[str, str] = {'f': format}

    def configure_audio(self, *,
                        rate:int = None,
                        codec:str = None,
                        bitrate:int = None):
        if rate is not None:
            self.__audio_flags['ar'] = f'{rate}'
        if codec is not None:
            self.__audio_flags['acodec'] = codec
        if bitrate is not None:
            self.__audio_flags['b:a'] = f'{bitrate}'
    
    def configure_video(self, *,
                        rate:int = None,
                        codec:str = None,
                        bitrate:int = None,
                        ):
        if rate is not None:
            self.__video_flags['r'] = f'{rate}'
        if codec is not None:
            self.__video_flags['vcodec'] = codec
        if bitrate is not None:
            self.__video_flags['b:v'] = f'{bitrate}'

    def create_ffmpeg_opts(self) -> List[str]:
        opts = []
        for key, value in self.__audio_flags.items():
            opts.append('-' + key)
            opts.append(value)
        for key, value in self.__video_flags.items():
            opts.append('-' + key)
            opts.append(value)
        opts.append(f'{self.__protocol}://{self.__hostname}:{self.__port}')
        return opts

    def set_port(self, port:int) -> None:
        self.__port = port
