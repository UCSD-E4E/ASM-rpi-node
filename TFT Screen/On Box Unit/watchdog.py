#import OB_v2
#from OB_v2 import On_Box_Window

from queue import Queue
import reset_screen
import os

#comm = "python3 reset_screen.py"

q = Queue(maxsize=2)

def grabqueueitem(gui):
    while True:
        try:
            item = q.get(timeout=5)
        except:
            print("baddie")
            gui.root.destroy()
            break
            

