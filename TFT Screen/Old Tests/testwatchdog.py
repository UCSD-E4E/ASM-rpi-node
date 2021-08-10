import datetime as dt
from threading import Thread
import time

watchdog_flag = 0

def func(flag):
    print("func started")
    while True:
        videoupdateflag(flag)
        for i in range(10):
            i=2
        
def timer_flagchange(flag):
    t_end = round(time.time() + 3) #3600 seconds in one hour
    #print("END TIME: " + str(t_end))

    while time.time() < t_end:
        #print("Counting Time: " + str(time.time()))
        if round(time.time()) == t_end: 
            flag = 1
            print("FLAG CHANGEDDD: " + str(int(flag)))

    print("end of timer and flag was changed")

def videoupdateflag(flag):
    if flag == 1:
        flag = 2
        print("flag = 2")

def evaluateflag(flag):
    print("EVALUATING FLAG")
    #time.sleep(5)
    if flag == 2:
        timer_flagchange(flag)
    else:
        print("need to quit and restart")
        return
    
timer_flagchange(watchdog_flag)

print("thread 1 start")
t1 = Thread(target=func, args=[watchdog_flag])
t1.start()

print("thread 2 start")
t2 = Thread(target=evaluateflag, args=[watchdog_flag])
t2.start()



