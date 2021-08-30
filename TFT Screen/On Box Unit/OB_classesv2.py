import tkinter as tk
from PIL import ImageTk, Image
import cv2
import datetime
import time

#from gpiozero import Button
#from threading import Thread

#button17 = Button("GPIO17")


class system_stats():
    def create_box(gui):
        gui.SystemBox = gui.canvas.create_rectangle(0,100,200,200, fill='light green')

class On_Box_Window:
    def start(self):
        self.root = tk.Tk()
        self.root.geometry("650x400")
        self.lmain = tk.Label(self.root)

        self.canvas = tk.Canvas(self.lmain, height= 200, width= 100)
        self.Arduino = self.canvas.create_rectangle(0,0,100,100,fill='green')
        self.canvas.create_window(0,0, window=self.lmain)

        self.lmain.pack()
        self.canvas.pack()
        self.canvas.place(relx=1.0, rely=0.0, anchor=tk.NE)
        
        system_stats.create_box(self)
       
    def notworking(self):
        self.Arduino = self.canvas.create_rectangle(0, 0, 100, 100, fill='red')
        self.canvas.itemconfig(self.Arduino, fill='red') 

    def mainloop(self):
#        self.root.after(time,fcn)
        self.root.mainloop()

    def repeat(self,time,fcn):
        self.root.after(time,fcn)

    def replytowatchdog(self):
        print("response still works")
        return 1
    
    def PIvideo_stream(self,cap):
        cap = cv2.VideoCapture(0)
        _,frame1 = cap.read()
        frame2 = cv2.resize(frame1,(1100,1000))
        font = cv2.FONT_HERSHEY_SIMPLEX
        datet = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        frame3 = cv2.putText(frame2,datet, (10,50), font, 1, (0,255,255),2, cv2.LINE_AA) 

        cv2image = cv2.cvtColor(frame3, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)
        self.lmain.after(50, self.PIvideo_stream)


#class buttonpush():
#    def __init__(self,gui):
#        self.b = False
#        self.gui = gui
        
#    def checkloop(self):
#        while True:
#            if button17.is_pressed:
#                if self.b == False:
#                    self.b = True
#                    self.gui.root.lower()
#                else:
#                    self.gui.root.lift()
#                    self.b = False
#                while button17.is_pressed: pass

#OB = On_Box_Window()
#OB.start()
#OB.PIvideo_stream()

#buttonclass = buttonpush(OB)
#check = Thread(target=buttonclass.checkloop)
#check.start()

#OB.mainloop()
