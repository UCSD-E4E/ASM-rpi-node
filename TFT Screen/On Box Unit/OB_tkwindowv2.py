import OB_v2
from OB_v2 import On_Box_Window
import Decoder2v7
from Decoder2v7 import *
from threading import Thread

ser = None
ser = serial.Serial('/dev/ttyACM0', 9600)
ser.flush()

#parser = binaryPacketParser()
#IMU_packets = parser.parseBytes(ser.read(88))
#aud_packets = parser.parseBytes(ser.read(1078))

def data_management():
    while(True):
        t_end = time.time() + 86400
        now = dt.datetime.now().strftime('%Y-%m-%d-%M-%S')
        csvname = 'IMUaudio'+ now + '.csv'
    
        with open(csvname,'w') as csvFile:
            while time.time() < t_end: 
                timestamp = dt.datetime.now()
                print("Start of loop stamp: " + str(timestamp))
                csvFile.write(str(timestamp)+'\n')

                parser = binaryPacketParser()
                IMU_packets = parser.parseBytes(ser.read(88))
                csvFile.write(str(IMU_packets)+'\n\n') 

                aud_packets = parser.parseBytes(ser.read(1078)) 
                csvFile.write(str(aud_packets)+'\n\n')

#                    gui.repeat(100, arduino_fnc) 

#                arduino_fnc()

gui = On_Box_Window()
gui.start()

gui.PIvideo_stream()

print("data thread starts")
data_thread = Thread(target=data_management)
data_thread.start()
print("data thread continues")

gui.mainloop()
 
