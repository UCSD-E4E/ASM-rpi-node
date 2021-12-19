import SensorNode.utils.audio as audio
import SensorNode.utils.video as video
import SensorNode.utils.rtp as rtp
import SensorNode.utils.ffmpeg as ffmpeg
import subprocess
import os
import json

def test_audio():
    test_time = 15
    if os.path.isfile('test.mp3'):
        os.remove('test.mp3')
    rx_ffmpeg = subprocess.Popen(
        ['ffmpeg', '-i', 'tcp://@:8500?listen', '-acodec', 'copy', '-flags', 
         '+global_header', '-reset_timestamps', '1', 'test.mp3']
    )
    audio_source = audio.HWAudioSource('hw:CARD=PCH,DEV=0', num_channels=2)
    audio_sink = rtp.RTPOutputStream('127.0.0.1', 8500)
    audio_sink.configure_audio(codec='libmp3lame', rate=48000)
    ffmpeg_config = ffmpeg.FFMPEGInstance(input_obj=audio_source, output_obj=audio_sink)
    ffmpeg_config.set_time(test_time)
    ffmpeg_cmd = ffmpeg_config.get_command()
    print(ffmpeg_cmd)
    subprocess.check_call(ffmpeg_cmd)
    assert(rx_ffmpeg.wait(test_time) == 0)
    
    test_file_params_json = subprocess.check_output(['ffprobe', '-i', 'test.mp3', '-hide_banner', '-show_format', '-show_streams', '-v', 'fatal', '-of', 'json']).decode()
    test_file_params = json.loads(test_file_params_json)
    assert(test_file_params['streams'][0]['codec_name'] == 'mp3')
    assert(int(test_file_params['streams'][0]['sample_rate']) == 48000)
    assert(int(test_file_params['streams'][0]['channels']) == 2)
    assert(abs(float(test_file_params['streams'][0]['duration']) - test_time) < 0.1)