from tkinter import *
import time 

#default is green meaning the screen works
#screen will turn red when an error occurs 

class Window:
    def __init__(self):
        self.root = Tk()
        self.root.geometry("320x240")
        self.canvas = Canvas(self.root, width=320, height= 240)
        self.Arduino = self.canvas.create_rectangle(280, 10, 310, 65, fill='green') 
        self.canvas.pack(fill=BOTH, expand=1) #check what this does 
        #self.root.mainloop()
        #self.root.update()
        #self.root.after(100, self.root.update()) #check what this does 
        
    def notworking(self):
        #self.Arduino = self.canvas.create_rectangle(280, 10, 310, 65, fill='red')
        self.canvas.itemconfig(self.Arduino, fill='red')
        self.root.update()
        #what do u want to happen after an error occurs? stop recording? send alert? 

    def mainloop(self):
        self.root.mainloop()


print("display begins")
gui = Window()

print("error occurred")
#Window.notworking(gui)

Window.mainloop(gui)

print("error occurred")
Window.notworking(gui)

