from Tkinter import *
import serial
import redis
import logging
import time
from VideoCapture import Device
import PIL
import prox

log = logging.getLogger(__name__)
#On the laptop, the Arduino enumerates as COM3
#I've specified the baud rate to be max (115200)

ser = serial.Serial("COM3", 115200) #I'm not going to specify a timeout so I can be blocking on the serial port
cam = Device()
red = redis.StrictRedis(host='localhost', port=6379, db=0)

class Entry:
    def __init__(self, master):
        self.frame = Frame(master)
        self.frame.pack()

        self.name_box = Text(frame)
        self.name_box.pack()

        self.picture = Label(frame)
        self.picture.pack()

        self.name_button = Button(frame, text="Submit Name/Take Photo", command=self.grab_name)
        self.name_button.pack()

        self.photo_button = Button(frame, text="Submit Photo", command=self.submit)


    def grab_name(self):
        self.name = self.name_box.get(0, 100)
        time.sleep(5)
        img = cam.getImage()
        photo = PIL.ImageTk.PhotoImage(img)
        self.picture.config(image=photo)

    def submit(self):
        if self.name is None:
            return
        self.red.set(line+".name", name)
        self.red.set(line+".status", 1)
        #TODO: store photo
        self.frame.quit()

def display_login(id_num, name, status):
    output = name+ ' [' +id_num+ '] '
    if status % 2:
        output += "++CHECKIN++"
    else:
        output += "--CHECKOUT--"
    print(output)
    #img_str = red.get(id_num+'.img')
    #img = PIL.Image.fromstring("RGBA", (1280, 720), img_str)
    #img.show("Face")
    log.info(output)

def run_loop():
    line = ser.readline().strip()
    if len(line) != 35:
        #TODO: log misread
        log.error("Line missized: ignoring")
        return
    if not check_parity(line):
        #TODO: log parity failure
        log.error("Parity error: ignoring")
        return
    #Check redis for the user with that id
    name = red.get(line+'.name')
    if name is not None:
        #If the user exists, toggle their in lab status and display that to them
        #Send an update hook to the itr website
        status = red.incr(line+'.status')
        display_login(line, name, status)
        pass
    else:
        #If they don't exist, prompt them to add themselves
        #      Field for name
        #      Display webcam
        #      On click (or something) take and display a picture to them
        #      After they approve it, store it somewhere, and make a new record for them
        #      Also, check them in
        name = raw_input("What is your name?")
        print("I will sleep 5 seconds, then take a picture of you.")
        print("Stand with your head in the box on the far wall")
        print("5...")
        time.sleep(1)
        print("4...")
        time.sleep(1)
        print("3...")
        time.sleep(1)
        print("2...")
        time.sleep(1)
        print("1...")
        time.sleep(1)
        img = cam.getImage()
        img.show()
        #TODO: actually display the photo
        red.set(line+".name", name)
        red.set(line+".status", 1)
        #red.set(line+".img",img)

def test_gui():
    root = Tk()
    gui = Entry(root)
    root.mainloop()
    root.destroy()
    time.sleep(5)

print "starting"
while True:
    test_gui()
