from gpiozero import Button
from time import sleep
import tkinter as tk
from threading import Thread

button17 = Button("GPIO17")
button22 = Button("GPIO22")
button23 = Button("GPIO23")
button27 = Button("GPIO27")

class buttonpush():
    
    def __init__(self):
        #Thread.__init__(self)
        self.b = False

    def checkloop(self):
        while True:
            if button17.is_pressed:
                if self.b == False:
                    self.b = True
                    print("pressed")
                    root.destroy()
                else:
                    self.b = False
                    print("off")
                while button17.is_pressed: pass 

#if button22.is_pressed:
#    print("button23 pressed")
#if button23.is_pressed:
#    print("button23 pressed")
#if button27.is_pressed:
#    print("button27 pressed")
print("before root")
root = tk.Tk()

print("before class made")
button17class = buttonpush()

print("before thread")
check17 = Thread(target=button17class.checkloop)
print("before start")
check17.start()
print("before mainloop")
root.mainloop() 
