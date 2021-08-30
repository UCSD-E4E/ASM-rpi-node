import yaml
from OB_classesv3 import On_Box_Window
#from RSU_classesv2 import RSU_Window
from threading import Thread
import serial.tools.list_ports
from glances_sub import system_specs
import watchdog 
import os
import OB_func

def read_yaml():
    with open(r'/boot/TFTscreenconfig.yaml') as file:
        gui = yaml.load(file, Loader=yaml.FullLoader) 
        return gui 

#class system_stats:
#    def create_OB(gui):
#        gui.SystemBox = gui.canvas.create_rectangle(0,100,200,200, fill='light green')

#    def create_RSU(gui):
#        gui.SystemBox = gui.canvas.create_rectangle(0,0,100,100, fill = 'light green')
        
#    def error(gui):
#        gui.SystemBox = gui.canvas.create_rectangle(0,100,200,200, fille='red')
#        gui.canvas.itemconfig(gui.SystemBox, fill='red')

gui = read_yaml()
print(str(gui))
RPi = system_specs()

if (str(gui) == "{'On_Box': True}"):
    dogqueue = watchdog.q

    OB = On_Box_Window()
    OB.start()
    #system_stats.create_OB(OB)
    OB.PIvideo_stream(dogqueue)

    system_thread = Thread(target=RPi.check_all, args=[OB])
    system_thread.start()

    data_thread = Thread(target=OB_func.data_management, args=[OB])
    data_thread.start()

    watchdog = Thread(target=watchdog.grabqueueitem, args=[OB])
    watchdog.start()

    OB.mainloop()

    comm = "python3 TFTscreen_v2.py"
    os.system(comm)

if (str(gui) == "{'Remote_Sensor': True}"):
    RSU = RSU_Window()
    RSU.start()
    #system_stats.create_RSU(RSU.self)
    RSU.IPvideo_stream()

    system_thread = Thread(target=RPi.check_all, args=[RSU])
    system_thread.start()

    RSU.mainloop()
 
