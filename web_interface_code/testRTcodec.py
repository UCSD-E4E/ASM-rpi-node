import codec
import serial
import binascii

codec = codec.Codec()
ser = serial.Serial("/dev/ttyACM0", 9600)
ser.flush()

while True:
    b = ser.read(1)
    bP = codec.decode(b)
    print(bP)
