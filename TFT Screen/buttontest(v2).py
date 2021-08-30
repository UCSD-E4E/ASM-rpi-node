from gpiozero import Button
from time import sleep
import tkinter as tk
from threading import Thread

button17 = Button("GPIO17")
button22 = Button("GPIO22")
button23 = Button("GPIO23")
button27 = Button("GPIO27")

#if button22.is_pressed:
#    print("button23 pressed")
#if button23.is_pressed:
#    print("button23 pressed")
#if button27.is_pressed:
#    print("button27 pressed")

class buttonpush():
    
    def __init__(self):
        #Thread.__init__(self)
        self.b = False

    def checkloop(self):
        while True:
            if button17.is_pressed:
                if self.b == False:
                    self.b = True
                    root.lower()
                else:
                    self.b = False
                while button17.is_pressed: pass

            if button22.is_pressed:
                if self.b == False:
                    self.b = True
                    root.lift()
                else:
                    self.b = False
                while button22.is_pressed: pass

root = tk.Tk()
buttonclass = buttonpush()
check = Thread(target=buttonclass.checkloop)
check.start()
root.mainloop() 
