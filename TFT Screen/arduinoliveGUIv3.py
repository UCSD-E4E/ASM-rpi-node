#default is green meaning the screen works
#screen will turn red when an error occurs 

from tkinter import *
import time

class Window:
    def start(self):
        self.root = Tk()
        self.root.title("Arduino Status")
        self.root.geometry("320x240")
        self.canvas = Canvas(self.root, width=320, height= 240)
        self.Arduino = self.canvas.create_rectangle(280, 10, 310, 65, fill='green') 
        self.canvas.pack(fill=BOTH, expand=1) 
        
    def notworking(self):
        self.Arduino = self.canvas.create_rectangle(280, 10, 310, 65, fill='red')
        self.canvas.itemconfig(self.Arduino, fill='red')

    def mainloop(self):
        self.root.mainloop()

    def repeat(self,time,fcn):
        self.root.after(time,fcn)

