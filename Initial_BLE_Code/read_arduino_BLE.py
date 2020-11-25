from bluepy.btle import UUID, Peripheral
import binascii
import struct
import datetime as dt
import sys

p = Peripheral("01:28:F6:D6:A5:E4")
GYROx_uuid = UUID(0x0004)
GYROy_uuid = UUID(0x0005) 
GYROz_uuid = UUID(0x0006)
#services = p.getServices()
#for service in services:
#    print (service)

try:
    ch = p.getCharacteristics(0x0004,0x0006)[0]
    if (ch.supportsRead()):
       #Sement of code handles (1) reading values from BLE (2) calculating its size  

       # while(1);
        start = dt.datetime.now()
       # for x in range(20):
       # val = binascii.b2a_hex(ch.read())           #size of val = 19
        val = ch.read()                            #size of val = 18
        end = dt.datetime.now()
        size = sys.getsizeof(val)                   #bytes
        val = binascii.b2a_hex(ch.read())


       #Segment of code prints the outputs nicely
        val = binascii.unhexlify(val)
        val = struct.unpack("b",val)[0]
        print (val)  


       #Segement of code (1)calculates throughput (2)prints all relevant variables 
        total_time_s = (end-start).total_seconds()
        throughput = size / total_time_s
        print("size")
        print(size)
        print("time")
        print(total_time_s)
        print("throughput")
        print(throughput)

finally:
    p.disconnect()

