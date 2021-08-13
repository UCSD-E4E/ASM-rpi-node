import time
from Decoder import *
import datetime as dt
import mailalert

mail = mailalert.MailAlert()

def concatenate_packet(string):
    st1 = string.replace(" ","")
    st2 = st1.rstrip("\n")
    st3 = st2.strip("[")
    st4 = st3.strip("]")
    return st4

def packet_len_time_check(IMUpack, audpack,starttime):
    if len(IMUpack) == 2 or len(audpack) == 2:
        gui.notworking()
        print("EMPTY PACKETS")
        mail.empty_emailalert()
        return

    else:
        timestamp_post = dt.datetime.now()
        #print("Timestamp_post: " + str(timestamp_post))
        time_diff = timestamp_post - starttime;
#        print("Timestamp: " + str(starttime))
        #print("TIME DIFFERENCE:" + str(time_diff))

        if (time_diff.total_seconds() > 8): 
            print("ERROR ERROR ERROR ERROR ERROR")
            mail.time_emailalert()
 #           print(time_diff.total_seconds())
            gui.notworking()
            return

def data_management(window):
    parser = binaryPacketParser()
    ser = serial.Serial("/dev/ttyACM0",9600)
    ser.flush()
    IMU_packets = parser.parseBytes(ser.read(88))
    aud_packets = parser.parseBytes(ser.read(1078))

    while(True):
        t_end = time.time() + 86400
        now = dt.datetime.now().strftime('%Y-%m-%d-%M-%S')
        binname = 'IMUaudio'+ now + '.bin'
    
        with open(binname,'w') as binFile:
            while time.time() < t_end: 
                timestamp = dt.datetime.now()
                TS = int(timestamp.timestamp() * 1e3) 
                packed = struct.pack("<Q", TS) 
                string = packed.hex().upper()
                length = 4
                time_s = '%s' % ''.join(string[i:i+length] for i in range(0, len(string),length))

                try:
                    IMU_packet = str(parser.parseBytes(ser.read(88)))
                    i = str(IMU_packet)
                    imu = concatenate_packet(i)
                    fin_imu = imu[:88] + time_s + imu[(88+len(time_s)):]
                    binFile.write(fin_imu)
                    
                    
                    aud_packet = str(parser.parseBytes(ser.read(1078))) 
                    a = str(aud_packet)
                    aud = concatenate_packet(a)
                    fin_aud = aud[:88] + time_s + aud[(88 + len(time_s)):]
                    aud = aud[:88] + time_s + aud[88 + len(time_s):]
                    binFile.write(fin_aud)

                    window.root.after(100, packet_len_time_check,IMU_packet,aud_packet, timestamp)

                except serial.SerialException:
                    window.notworking()
                    mail.serial_connect_emailalert()
                    print("ERRRRORRR") 
                    return None




#comm = "python3 allmightydog.py"
#os.system(comm)


#if __name__ == "__main__":
#    main()
 
