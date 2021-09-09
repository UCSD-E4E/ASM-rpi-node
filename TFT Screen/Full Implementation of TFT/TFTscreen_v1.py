from gpiozero import Button
import tkinter as tk
from PIL import ImageTk, Image
from threading import Thread
import cv2
import yaml
import datetime

button17 = Button("GPIO17")
button22 = Button("GPIO22")

class On_Box_Window:
    def start(self):
        self.root = tk.Tk()
        self.root.geometry("650x400") 
        self.lmain = tk.Label(self.root)

        self.canvas = tk.Canvas(self.lmain, width = 100, height = 100)
        self.Arduino = self.canvas.create_rectangle(0,0,100,100,fill='green')
        self.canvas.create_window(0,0, window=self.lmain)
        self.lmain.pack()
        self.canvas.pack()
        self.canvas.place(relx = 1.0, rely = 0.0, anchor= tk.NE)

    def notworking(self):
        self.Arduino = self.canvas.create_rectangle(280, 10, 310, 65, fill='red')
        self.canvas.itemconfig(self.Arduino, fill='red')

    def mainloop(self):
        self.root.mainloop()

    def repeat(self,time,fc):
        self.root.after(time,fcn)

    def PIvideo_stream(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FPS, 10)
        ret,frame1 = cap.read()
        
        if ret:
            small_frame = cv2.resize(frame1, None, fx=0.25, fy=0.25)
        else:
            pass

        frame2 = cv2.resize(frame1,(1100,1000))
#        frame2 = cv2.resize(frame1,(500,500))
        font = cv2.FONT_HERSHEY_SIMPLEX
        datet = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        frame3 = cv2.putText(frame2, datet, (10,50), font, 1, (0,255,255),2,cv2.LINE_AA)
                
        cv2image = cv2.cvtColor(frame3, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)
        self.lmain.after(50, self.PIvideo_stream)

class RSU_Window:
    def start(self):
        self.root = tk.Tk()
        self.app = tk.Frame(self.root)
        self.app.grid()
        self.lmain = tk.Label(self.app)
        self.lmain.grid()

    def mainloop(self):
        self.root.mainloop()

    def IPvideo_stream(self):
        cap = cv2.VideoCapture("rtsp://admin:NyalaChow22@192.168.2.64:554/live.sdp")
        _,frame = cap.read()
        frame = cv2.resize(frame,(620,390))
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)
        self.lmain.after(100, self.IPvideo_stream)

class buttonpush(): 
    def __init__(self,gui):
        self.b = False
        self.gui = gui

    def checkloop(self):
        while True:
            if button17.is_pressed:
                if self.b == False:
                    self.b = True
                    self.gui.root.lower()
                else:
                    self.b = False
                while button17.is_pressed: pass

            if button22.is_pressed:
                if self.b == False:
                    self.b = True
                    self.gui.root.lift()
                else:
                    self.b = False
                while button22.is_pressed: pass

class read_yaml:
    def read():
        with open(r'/boot/TFTscreenconfig.yaml') as file:
            gui = yaml.load(file, Loader=yaml.FullLoader) 
            return gui

gui = read_yaml.read()
print(str(gui))

if (str(gui) == "{'On_Box': True}"):
    OB = On_Box_Window()
    OB.start()
#    cap = cv2.VideoCapture(0)
    OB.PIvideo_stream()

    buttonclass = buttonpush(OB)
    check = Thread(target=buttonclass.checkloop)
    check.start()

    OB.mainloop()

if (str(gui) == "{'Remote_Sensor': True}"):
    RSU = RSU_Window()
    RSU.start()
    RSU.IPvideo_stream()

    buttonclass = buttonpush(RSU)
    check = Thread(target=buttonclass.checkloop)
    check.start()

    RSU.mainloop()
 
