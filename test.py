#Import necessary Library
from tkinter import *
from tkinter.filedialog import asksaveasfile

#Create an instance of tkinter window
win= Tk()

#Set the geometry of tkinter window
win.geometry("750x250")

#Define the function
def save_file():
   f = asksaveasfile(initialfile = 'Untitled.txt',
defaultextension=".txt",filetypes=[("All Files","*.*"),("Text Documents","*.txt")])

#Create a button
btn= Button(win, text= "Save", command= lambda:save_file())
btn.pack(pady=10)

win.mainloop()