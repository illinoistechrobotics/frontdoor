from Tkinter import *
import serial
import redis
import logging
import time
from VideoCapture import Device
import PIL
import PIL.ImageTk
import prox

log = logging.getLogger(__name__)
#On the laptop, the Arduino enumerates as COM3
#I've specified the baud rate to be max (115200)

ser = serial.Serial("COM3", 115200) #I'm not going to specify a timeout so I can be blocking on the serial port
cam = Device()
red = redis.StrictRedis(host='localhost', port=6379, db=0)

class PhotoEntry:
    def __init__(self, master, id_num):
        self.id_num = id_num 
        
        self.frame = Frame(master)
        self.frame.pack()

        self.instructions = Label(self.frame, text="Enter your name in the box, then click 'Take Photo.' The shutter will release 5 seconds after you click that button.")
        self.instructions.pack()

        self.name_box = Entry(self.frame)
        self.name_box.pack(fill=X)

        self.name_button = Button(self.frame, text="Take Photo (5 second delay)", command=self.grab_name)
        self.name_button.pack(fill=X)

        self.photo_button = Button(self.frame, text="Submit Photo", state=DISABLED, command=self.submit)
        self.photo_button.pack(fill=X)

        self.picture = None
        self.img_string = ""

    def grab_name(self):
        self.name = self.name_box.get()
        time.sleep(5)
        img = cam.getImage()
        self.img_string = img.tostring()
        img.thumbnail((800,600), PIL.Image.ANTIALIAS)
        photo = PIL.ImageTk.PhotoImage(img)
        if self.picture is not None:
            self.picture.destroy()
        self.picture = Label(self.frame, image=photo)
        self.picture.image = photo
        self.picture.pack()
        self.photo_button.config(state=NORMAL)
        self.instructions.config(text="If you are happy with the photo, click 'Submit Photo', otherwise take a new photo")

    def submit(self):
        if self.name is None:
            return
        red.set(self.id_num+".name", self.name)
        red.set(self.id_num+".status", 1)
        red.set(self.id_num+".img",self.img_string)
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
    gui = PhotoEntry(root)
    root.mainloop()
    root.destroy()
    time.sleep(5)

print "starting"
while True:
    print "top of gui"
    test_gui()
    print "bottom of gui"
