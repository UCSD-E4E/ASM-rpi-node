import tkinter as tk

class Test():
    def __init__(self):
        self.root = tk.Tk()
        button = tk.Button(self.root, text = 'click', command=self.quit)
        button.pack()
        self.root.mainloop()

    def quit(self):
        self.root.destroy()

app = Test()
