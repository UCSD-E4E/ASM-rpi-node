from tkinter import *
import Decoder2
import time

#display window first (intialize w/ green signals) 
#read the flag 
#if flag == works, blink green
#if flag == no working, keep box red forever - then exit? 

class Window: 
    def __init__(self):
        self.root = Tk(className='Display Baby')
        self.root.geometry("320x240")
        self.root.configure(bg='white')
        self.canvas = Canvas(self.root, width=320, height= 240)
        self.PiIR = self.canvas.create_rectangle(0, 0, 270, 240, fill='blue')
        self.IMUPDM = self.canvas.create_rectangle(280, 10, 310, 65, fill='green')
        self.PiMic = self.canvas.create_rectangle(280, 140, 310, 195, fill='green')
        self.canvas.pack(fill=BOTH, expand=1)
        #self.root.mainloop()
        self.root.after(100, self.root.update()) 

    def notworkingflag(self):
        self.IMUPDM = self.canvas.create_rectangle(280, 10, 310, 65, fill='red')
        self.root.update()
        time.sleep(50000)
        #what do u want to happen after an error occurs? stop recording? send alert?

    def workingflag(self): #blinking effect 
        self.IMUPDM = self.canvas.create_rectangle(280, 10, 310, 65, fill='white')
        self.root.update() 
        time.sleep(0.5)
        self.IMUPDM = self.canvas.create_rectangle(280, 10, 310, 65, fill='green')
        self.root.update()
        time.sleep(0.5)
        self.IMUPDM = self.canvas.create_rectangle(280, 10, 310, 65, fill='white')
        self.root.update() 
        time.sleep(0.5)
        self.IMUPDM = self.canvas.create_rectangle(280, 10, 310, 65, fill='green')
        self.root.update() 
        time.sleep(0.5)

#    def refreshgui(self):
#        self.root.update()
#        time.sleep(2)

def Decodertest(gui):
#instead of while loop in Decoder2.py you need to implement the while loop in here --> in decoder, have it read once 
#would writin to a text file work better here? 
    if(Decoder2.bestfunction() == 1):
        print("display_flag =")
        print(Decoder2.bestfunction())
        gui.workingflag()
    elif (Decoder2.bestfunction() == -1):
        print("display_flag =")
        print(Decoder2.bestfunction())
        gui.notworkingflag()
    else:
        print("Something is very very wrong, the return value is not expected")

#while(True):
print("Display Begins")
gui = Window()

print("Sensor is working...")
Decodertest(gui)
#test whether while loop in Decodertest is faster or slower than while loop in Decoder2

print("Sensor not working...")
print("display_flag= ")
print("-1")
gui.notworkingflag()

#print("refreshing")
#gui.refreshgui()
