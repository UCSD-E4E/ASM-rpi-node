import tkinter as tk
from PIL import ImageTk, Image
import cv2
import datetime
import time
#import watchdog
from threading import Thread

#from gpiozero import Button
#from threading import Thread

#button17 = Button("GPIO17")

class system_stats:
    def create_box(gui):
        gui.SystemBox = gui.canvas.create_rectangle(0,100,200,200, fill='light green')

    def error(gui):
        gui.SystemBox = gui.canvas.create_rectangle(0,100,200,200, fill='red') 
        gui.canvas.itemconfig(gui.SystemBox, fill='red')

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
    
    def sys_notworking(self):  
        self.sysbox = self.canvas.create_rectangle(0,100,200,200,fill='red')
        system_stats.error(self)

    def notworking(self):
        self.Arduino = self.canvas.create_rectangle(0, 0, 100, 100, fill='red')
        self.canvas.itemconfig(self.Arduino, fill='red')

    def mainloop(self):
#        self.root.after(time,fcn)
        self.root.mainloop()

    def repeat(self,time,fcn):
        self.root.after(time,fcn)

    def PIvideo_stream(self, queue): 
        cap = cv2.VideoCapture(0)

        def showvideo():
            queue.put('1')

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
            self.lmain.after(50, self.PIvideo_stream, queue)
        
        
                #print(queue.qsize())
        showvideo() 


#OB = On_Box_Window()
#OB.start()
#OB.PIvideo_stream()

#buttonclass = buttonpush(OB)
#check = Thread(target=buttonclass.checkloop)
#check.start()

#OB.mainloop()
