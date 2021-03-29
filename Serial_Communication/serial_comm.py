import serial
import struct
import time

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0', 9600)
    file1 = open("Serial_Data.txt","w+")

    while(True):
        ser.flush()
        if ser.in_waiting >0:
            for y in range(6):
                accgyr = ser.read(4)
                print(struct.unpack('f',accgyr))
            
            for x in range(256):
                mic = ser.read(2)
                print(struct.unpack('h',mic))

            print("done")

