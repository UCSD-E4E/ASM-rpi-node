import serial
import datetime as dt

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0', 115200)
    #ser.flush()
    
    while True:
        if ser.in_waiting > 0:
            start = dt.datetime.now()
            line = ser.readline()
            end = dt.datetime.now()
            print(line)
            break
    total_time_s = (end - start).total_seconds()
    throughput = 100 / total_time_s
    print("time")
    print(total_time_s)
    print("Throughput is ")
    print(throughput)
