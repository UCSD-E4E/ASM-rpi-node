#from tkinter import *
import tkinter as tk 
from PIL import ImageTk, Image, ImageDraw
import cv2
import datetime

datet = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 
root = tk.Tk()
#app = tk.Frame(root, bg="white")
#app.gri)
lmain=tk.Label(root)

#canvas= tk.Canvas(lmain)
#Arduino = canvas.create_rectangle(1000,0,1050,100,fill='green')

lmain.pack()
#canvas.pack(expand= 1, fill= tk.BOTH)



def video_stream():
    cap = cv2.VideoCapture(0)
#    cap.set(cv2.CAP_PROP_FPS, 10)
    ret,frame = cap.read()
    frame = cv2.resize(frame, (1100, 1000))
    font = cv2.FONT_HERSHEY_SIMPLEX
    datet = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 
    frame =  cv2.putText(frame, datet, (10,50), font,1, (0,255,255), 2, cv2.LINE_AA)   
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(50, video_stream)

    fps = int(cap.get(5))
    print(fps)

video_stream()
root.mainloop()
