import tkinter as tk
import numpy as np
from PIL import ImageTk, Image
import cv2
import datetime
import time
from threading import Thread

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
        
    def mainloop(self):
#        self.root.after(time,fcn)
        self.root.mainloop()

    #def PIvideo_stream(self, queue): 
    def PIvideo_stream(self):  
        cap = cv2.VideoCapture(0)
        if (cap.isOpened() == False):
            print("Error opening video stream")

        if (cap.isOpened()):
            ret,frame1 = cap.read()
            if ret == True:
                font = cv2.FONT_HERSHEY_SIMPLEX
                datet = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                frame3 = cv2.putText(frame1,datet, (10,50), font, 1, (0,255,255),2, cv2.LINE_AA)
                cv2image = cv2.cvtColor(frame3, cv2.COLOR_BGR2RGBA)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                self.lmain.imgtk = imgtk
                self.lmain.configure(image=imgtk)
                #self.lmain.after(50, self.PIvideo_stream, queue)
                self.lmain.after(50, self.PIvideo_stream)
            else:
                print("ret == False")
                cap.release()
                cap = cv2.VideoCapture(0)
                ret, frame1 = cap.read()
                print("ret after: " + ret)

                 
        #cap.release()
        #cv2.destroyAllWindows()

#print("before OB")
OB = On_Box_Window()

#print("before start")
OB.start()

#print("video start")
OB.PIvideo_stream()

OB.mainloop()
