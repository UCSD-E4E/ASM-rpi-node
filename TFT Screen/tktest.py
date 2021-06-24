import subprocess
import tkinter

root = Tk()
app = Frame(root, bg="white")
app.grid()
lmain = Label(app)
lmain.grid()

cmd = "raspistill -t 0"



