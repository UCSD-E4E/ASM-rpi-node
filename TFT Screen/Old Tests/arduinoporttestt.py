import serial.tools.list_ports

while(True):
    all_ports = serial.tools.list_ports.comports()
    port_list = [] 
    for port, desc, hwid in sorted(all_ports): 
        port_list.append(port)
    
        #print("{}: {} [{}]".format(port, desc, hwid))

    if "/dev/ttyACM0" in port_list:
        print("still connected")
    else:
        print("ERROR")
#import serial 
#import time

#ser = serial.Serial()
#ser.baudrate = 9600
#ser.port = "/dev/ttyACM0"
#ser.open()

#print(ser.name)
#while (True):
#    if ser.isOpen() == False:
#        print("error")
#    else:
#        print("ERROR")
#ser.close()


