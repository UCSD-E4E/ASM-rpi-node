import psutil
import OB_classesv3
from OB_classesv3 import On_Box_Window
from threading import Thread
import mailalert

mail = mailalert.MailAlert()

class system_specs:
    def cpu_check(self):
        cpu_percent = psutil.cpu_percent(1)
        if round(cpu_percent) > 80:
            print("CPU PERCENT HIGH:" + str(cpu_percent)) 
            return 0
        else: 
            return 1
            #print("cpu good: " + str(cpu_percent))

    def memory(self):
        memory = psutil.virtual_memory()
        if round(memory.percent) > 60:
            print("MEMORY PERCENT ERROR:" + str(memory.percent))
            return 0
        else:
            return 1
            #print("good memory %: " + str(memory.percent))

    def disk(self):
        disk = psutil.disk_usage('/')
        if round(disk.percent) > 60:
            print("DISK PERCENT ERROR:" + str(disk.percent))
            return 0
        else:
            return 1
            #print("good disk %: " + str(disk.percent))

    def temp(self):
        cpu_temp = psutil.sensors_temperatures()["cpu_thermal"][0].current
        if cpu_temp > 50:
            print("ERROR TEMP HIGHH: " + str(cpu_temp))
            return 0
        else:
            #print("ERROR TEMP HIGHH: " + str(cpu_temp))
            return 1
            #print("Good temp: " + str(cpu_temp))

    def check_all(self,window):
        while(True):
            if self.cpu_check() == 0 or self.memory() == 0 or self.disk() == 0 or self.temp() == 0:
                window.sys_notworking()
                mail.glances_emailalert()
                #print("CPU:" + str(self.cpu_check()))
                #print("Memory:" + str(self.memory()))
                #print("Disk: "+ str(self.disk()))
                #print("temperature: " + str(self.temp()))

            else:
                #print("CPU:" + str(self.cpu_check()))
                #print("Memory:" + str(self.memory()))
                #print("Disk: "+ str(self.disk()))
                #print("temperature: " + str(self.temp()))
                pass
            #window.root.after(100, self.check_all2, self.window)

#gui = On_Box_Window()
#gui.start()
#gui.PIvideo_stream()

#RPi = system_specs()
#checkthread = Thread(target=RPi.check_all, args=[gui])
#checkthread.start()

#gui.mainloop()

#while(True):
#    print("CPU:" + str(RPi.cpu_check()))
#    print("Memory:" + str(RPi.memory()))
#    print("Disk: "+ str(RPi.disk()))
    #print("temperature: " + str(RPi.temp()))


#while(True):
 #   print("CPU Percent: " + str(psutil.cpu_percent(1)))

#        available = round(memory.available/1024.0/1024.0, 1)
#    total = round(memory.total/1024.0/1024.0, 1)
#    print("Total Memory: " + str(total) + "MB")
#    print("Available Memory: " + str(available) "MB")
#    print(str(available) + 'MB free /' + str(total) + 'MB total (' + str(memory.percent) + '%)')
#    print("Memory Percent: " + str(memory.percent))

    
#    free = round(disk.free/1024.0/1024.0/1024.0, 1)
#    total = round(disk.total/1024.0/1024.0/1024.0, 1)
#    print(str(free) + 'GB free /' + str(total) + 'GB total (' +  str(disk.percent) + '%)')
#    print("Disk Percent: " + str(disk.percent))

