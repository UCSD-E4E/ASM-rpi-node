import yaml
from OB_classesv3 import On_Box_Window
from RSU_classesv2 import RSU_Window
import Decoder
from threading import Thread
import serial.tools.list_ports
from glances_sub import system_specs
import watchdog 
import os
import time
import datetime as dt

def packet_len_time_check(IMUPack, audpack, starttime):
    if len(IMUpack) == 2 or len(audpack) == 2:
        gui.notworking()
        print("EMPTY PACKETS")
        return 

    else: 
        timestamp_post = dt.datetime.now()
        time_diff = timestamp_post - starttime;

        if (time_diff.total_seconds() > 8):
            print("LONGER THAN 8 SECONDS B/W PACKETS")
            gui.notworking()
            return

def data_management(window):
    while(True):
        t_end = time.time() + 86400
        now = dt.datetime.now().strftime('%Y-%m-%d-%M-%S')
        csvname = 'IMUaudio' + now + '.csv'

        with open(csvname, 'w') as csvFile:
            while time.time() < t_end:
                timestamp = dt.datetime.now()
                csvFile.write(str(timestamp) + '\n')

                try:
                    IMU_packet = parser.parseBytes(ser.read(88))
                    csvFile.write(str(IMU_packet) + '\n\n')

                    aud_packet = parser.parseBytes(ser.read(1079))
                    csvFile.write(str(aud_packet) + '\n\n')

                    window.root.afterr(100, packet_len_time_check, IMU_packet, aud_packet, timestamp)

                except serial.SerialException:
                    window.notworking()
                    print("Arduino USB connection is broken") 
                    return None

def read_yaml():
    with open(r'/boot/TFTscreenconfig.yaml') as file:
        gui = yaml.load(file, Loader=yaml.FullLoader) 
        return gui 

gui = read_yaml()
print(str(gui))

if (str(gui) == "{'On_Box': True}"):
    ser = serial.Serial("/dev/ttyACM0", 9600)
    ser.flush()
    parser = Decoder.binaryPacketParser()
    IMU_packet = parser.parseBytes(ser.read(88))
    aud_packet = parser.parseBytes(ser.read(1078))
    dogqueue = watchdog.q

    OB = On_Box_Window()
    OB.start()
    OB.PIvideo_stream(dogqueue)

    RPi = system_specs()
    system_thread = Thread(target=RPi.check_all, args=[OB])
    system_thread.start()

    data_thread = Thread(target=data_management, args=[OB])
    data_thread.start()

    watchdog = Thread(target=watchdog.grabqueueitem, args=[OB])
    watchdog.start()

    OB.mainloop()

    comm = "python3 TFTscreen_v2.py"
    os.system(comm)

if (str(gui) == "{'Remote_Sensor': True}"):
    RSU = RSU_Window()
    RSU.start()
    RSU.IPvideo_stream()

    RSU.mainloop()
 
