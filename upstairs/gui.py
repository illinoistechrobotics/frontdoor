#!/usr/bin/python3
import logging
import os
from tkinter import *

import PIL.Image
import PIL.ImageTk
import prox
import redis
import serial

log = logging.getLogger(__name__)
# On the laptop, the Arduino enumerates as COM3
# I've specified the baud rate to be max (115200)

ser = serial.Serial("/dev/ttyACM0",
                    115200)  # I'm not going to specify a timeout so I can be blocking on the serial port
red = redis.StrictRedis(host='localhost', port=6379, db=0)

class PhotoEntry:
    def __init__(self, master, id_num):
        self.id_num = id_num
        
        self.frame = Frame(master)
        self.frame.pack()

        self.instructions = Label(self.frame, text="Enter your name in the box, then click 'Take Photo.' The shutter will release 5 seconds after you click that button.")
        self.instructions.pack()

        self.name_box = Entry(self.frame)
        self.name_box.focus_set()
        self.name_box.pack(fill=X)

        self.name_button = Button(self.frame, text="Take Photo (5 second delay)", command=self.grab_name)
        self.name_button.pack(fill=X)

        self.photo_button = Button(self.frame, text="Submit Photo", state=DISABLED, command=self.submit)
        self.photo_button.pack(fill=X)

        master.bind("<Return>", lambda x: (self.grab_name() if self.picture is None else self.submit()))

        self.picture = None
        self.img_string = ""

    def grab_name(self):
        self.name = self.name_box.get()

        os.system('mpv --length=5 /dev/video0')

        os.system('ffmpeg -f v4l2 -i /dev/video0 -video_size 1280x720 -vframes 1 temp_image.png -y')

        img = PIL.Image.open("temp_image.png")
        photo = PIL.ImageTk.PhotoImage(img)
        if self.picture is not None:
            self.picture.destroy()
        self.picture = Label(self.frame, image=photo)
        self.picture.image = photo
        self.picture.pack()
        self.img_string = img.tobytes()
        self.photo_button.config(state=NORMAL)
        self.instructions.config(text="If you are happy with the photo, click 'Submit Photo', otherwise take a new photo")

    def submit(self):
        if self.name is None or self.img_string is "":
            return
        red.set(str(self.id_num) + ".name", self.name)
        red.set(str(self.id_num) + ".status", 1)
        red.set(str(self.id_num) + ".img", self.img_string)
        red.sadd("inlab",self.id_num)
        self.frame.quit()

class Login:
    def __init__(self,master,id_num):
        frame = Frame(master)
        frame.pack()

        topline = "%s\n[%s]" % (red.get("%s.name" % str(id_num)), str(id_num))
        nameline = Label(frame, text=topline, bg="black", fg="white", font = "Monospace 30")
        nameline.pack(fill=X)

        status = int(red.get(str(id_num) + '.status'))
        if status % 2:
            statusline = Label(frame, text="CHECKIN", bg="black", fg="green", font="Monospace 30")
            statusline.pack(fill=X)
            red.sadd("inlab",id_num)
        else:
            statusline = Label(frame, text="CHECKOUT", bg="black", fg="red", font = "Monospace 30")
            statusline.pack(fill=X)
            red.srem("inlab",id_num)

        img_str = red.get(str(id_num) + '.img')
        if img_str is not None:
            img = PIL.Image.frombytes('RGB', (1280, 720), img_str)
            photo = PIL.ImageTk.PhotoImage(img)
            picture = Label(frame, image=photo)
            picture.image = photo
            picture.pack()      
            

def display_login(id_num):
    root = Tk()
    gui = Login(root,id_num)
    root.after(5000, lambda: root.destroy())
    root.mainloop()
    
def run_entry(id_num):
    root = Tk()
    gui = PhotoEntry(root,id_num)
    root.mainloop()
    root.destroy()
    
def run_loop():
    id_num = ser.readline().strip()
    if len(id_num) != 35:
        #TODO: log misread
        log.error("Line missized: ignoring")
        return
    if not prox.check_parity(id_num):
        #TODO: log parity failure
        log.error("Parity error: ignoring")
        return
    #Check redis for the user with that id
    name = red.get(str(id_num) + '.name')
    if name is not None:
        #If the user exists, toggle their in lab status and display that to them
        #Send an update hook to the itr website
        status = red.incr(str(id_num) + '.status')
        display_login(id_num)
    else:
        #If they don't exist, prompt them to add themselves
        #      Field for name
        #      Display webcam
        #      On click (or something) take and display a picture to them
        #      After they approve it, store it somewhere, and make a new record for them
        #      Also, check them in
        run_entry(id_num)

while True:
    run_loop()
