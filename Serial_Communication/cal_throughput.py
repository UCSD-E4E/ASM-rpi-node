import serial
import datetime as dt

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0', 1000000)
    #ser.flush()
    
    num_bytes = 0
    total_time_s = 0
    
    while (total_time_s < 10):
        if ser.in_waiting > 0:
            start = dt.datetime.now()
            line = ser.read()
            end = dt.datetime.now()
            num_bytes += 1
            total_time_s = total_time_s + (end - start).total_seconds()
    throughput = num_bytes / total_time_s
    print("Number of bytes")
    print (num_bytes)
    print("time")
    print(total_time_s)
    print("Throughput is ")
    print(throughput)
