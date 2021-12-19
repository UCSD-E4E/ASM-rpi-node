import re
import subprocess
from typing import Dict, List

from SensorNode.utils.ffmpeg import MediaInput


class HWAudioSource(MediaInput):
    def __init__(self, id:str, *,num_channels:int=1, sample_rate:int=48000) -> None:
        self.__id = id
        if self.__id not in self.get_input_devices():
            raise RuntimeError("Invalid ID")
        self.__num_channels = num_channels
        self.__sample_rate = sample_rate

    @staticmethod
    def get_input_devices() -> Dict[str, str]:
        arecord_output = subprocess.check_output(['arecord', '-L']).decode('ascii', 'ignore')
        card_regex = r"^(?P<device>[^\s]*)\n\s*(?P<desc>.*)"
        matches = re.finditer(card_regex, arecord_output, re.MULTILINE)
        cards = {match.group('device'): match.group('desc') for match in matches}

        return cards

    def create_ffmpeg_opts(self) -> List[str]:
        return ['-f', 'alsa', '-channels', f'{self.__num_channels}', '-sample_rate', f'{self.__sample_rate}', '-i', self.__id]

    def set_num_channels(self, num_channels:int):
        self.__num_channels = num_channels

if __name__ == '__main__':
    print(HWAudioSource.get_input_devices())
