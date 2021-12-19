import SensorNode.utils.audio as audio
import SensorNode.utils.video as video
import SensorNode.utils.rtp as rtp
import SensorNode.utils.ffmpeg as ffmpeg
import subprocess
import os

def test_audio():
    os.remove('test.mp3')
    rx_ffmpeg = subprocess.Popen(
        ['ffmpeg', '-i', 'tcp://@:8500?listen', '-acodec', 'copy', '-flags', 
         '+global_header', '-reset_timestamps', '1', 'test.mp3']
    )
    audio_source = audio.HWAudioSource('hw:CARD=PCH,DEV=0', num_channels=2)
    audio_sink = rtp.RTPOutputStream('127.0.0.1', 8500)
    audio_sink.configure_audio(codec='libmp3lame', rate=48000)
    ffmpeg_config = ffmpeg.FFMPEGInstance(input_obj=audio_source, output_obj=audio_sink)
    ffmpeg_config.set_time(30)
    ffmpeg_cmd = ffmpeg_config.get_command()
    print(ffmpeg_cmd)
    subprocess.check_call(ffmpeg_cmd)
    assert(rx_ffmpeg.wait(30) == 0)
