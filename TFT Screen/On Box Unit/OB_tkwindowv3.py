import OB_v2
from OB_v2 import On_Box_Window
import Decoder2v7
from Decoder2v7 import *
from threading import Thread
import serial.tools.list_ports
import glancesval
from glancesval import system_specs
import watchdog

ser = serial.Serial("/dev/ttyACM0",9600)
ser.flush()

parser = binaryPacketParser()
#First time running the Decoder will give empty packets, so throw those away immediately.
IMU_packets = parser.parseBytes(ser.read(88))
aud_packets = parser.parseBytes(ser.read(1078))

def packet_len_time_check(IMUpack, audpack,starttime):
    if len(IMUpack) == 2 or len(audpack) == 2:
        gui.notworking()
        print("EMPTY PACKETS")
        return

   #            elif(csvFile.closed):
   #                 gui.notworking()
   #                 return

    else:
        timestamp_post = dt.datetime.now()
        print("Timestamp_post: " + str(timestamp_post))
        time_diff = timestamp_post - starttime;
#        print("Timestamp: " + str(starttime))
        print("TIME DIFFERENCE:" + str(time_diff))

        if (time_diff.total_seconds() > 8): 
            print("ERROR ERROR ERROR ERROR ERROR")
 #           print(time_diff.total_seconds())
            gui.notworking()
            return

def data_management(window):
    while(True):
        t_end = time.time() + 86400
        now = dt.datetime.now().strftime('%Y-%m-%d-%M-%S')
        csvname = 'IMUaudio'+ now + '.csv'
    
        with open(csvname,'w') as csvFile:
            while time.time() < t_end: 
                timestamp = dt.datetime.now()
                print("Start of loop stamp: " + str(timestamp))
                csvFile.write(str(timestamp)+'\n')

                try:
                    IMU_packets = parser.parseBytes(ser.read(88))
                    csvFile.write(str(IMU_packets)+'\n\n') 

                    aud_packets = parser.parseBytes(ser.read(1078)) 
                    csvFile.write(str(aud_packets)+'\n\n')

                    window.root.after(100, packet_len_time_check,IMU_packets,aud_packets, timestamp) 
                except serial.SerialException:
                    window.notworking()
                    print("ERRRRORRR") 
                    return None


gui = On_Box_Window()
gui.start()

gui.PIvideo_stream()

RPi = system_specs()
system_thread = Thread(target=RPi.check_all,args=[gui])
system_thread.start()

data_thread = Thread(target=data_management,args=[gui])
data_thread.start()

gui.mainloop()
 
