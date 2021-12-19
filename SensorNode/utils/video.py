from typing import List, Optional
from SensorNode.utils.ffmpeg import MediaInput


class VideoSource(MediaInput):
    pass

class RTSPVideoSource(VideoSource):
    def __init__(self, user: str, passwd: str, hostname:str, port:int, sdp_path:str = ''):
        self.__uri = f'rtsp://{user}:{passwd}@{hostname}:{port}/{sdp_path}'

    def create_ffmpeg_opts(self) -> List[str]:
        return ['-i', self.__uri]

class HWVideoSource(VideoSource):
    def __init__(self, handle: str, *, channel:Optional[int]=None, video_size:Optional[str]=None) -> None:
        self.__handle = handle

    def create_ffmpeg_opts(self) -> List[str]:
        return ['-f', 'video4linux2', '-i', self.__handle]