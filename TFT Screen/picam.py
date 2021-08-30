from tkinter import *
from PIL import ImageTk, Image
import cv2

root = Tk()
app = Frame(root, bg="white")
app.grid()
lmain=Label(app)
lmain.grid()

cap=cv2.VideoCapture(0)

def video_stream():
	_, frame = cap.read()
	cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
	img = Image.fromarray(cv2image)
	imgtk = ImageTk.PhotoImage(image=img)
	lmain.imgtk = imgtk
	lmain.configure(image=imgtk)
	lmain.after(1, video_stream)

video_stream()
root.mainloop()
