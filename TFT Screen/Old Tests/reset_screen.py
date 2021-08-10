import os 
import time 
import sys

def reset_screen(gui,thread):
    #gui.root.destroy()
    #thread.join()

    command_restart = "python3 allmightydog.py"
    #os.system(command_restart)

    #time.sleep(4) 

    command_killscreen = "pkill -f allmightydog"
    os.system()



    
    #command_compilearduino = "arduino-cli compile -b arduino:mbed:nano33ble audIMU"
    #os.system(command_compilearduino)

    #command_uploadarduino = "arduino-cli upload -p /dev/ttyACM0 -b arduino:mbed:nano33ble audIMU"
    #os.system(command_uploadarduino)

    #time.sleep(3)
#    command_restart = "python3 allmightydog.py"
#    os.system(command_restart)
#def reset_screen():


