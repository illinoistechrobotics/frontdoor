#!/usr/bin/python3
import datetime
import logging
import os
#import serial
import configparser
from tkinter import *

import PIL.Image
import PIL.ImageTk
import prox
from sqlalchemy import Column, Integer, String, DateTime, LargeBinary, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

log = logging.getLogger(__name__)
# On the laptop, the Arduino enumerates as COM3
# I've specified the baud rate to be max (115200)

config = configparser.ConfigParser()
if not config.read('config.cfg'):
    config.add_section('Serial')
    config.set('Serial', 'Baud', '115200')
    config.set('Serial', 'Port', '/dev/ttyACM0')

    config.add_section('Database')
    config.set('Database', 'ConnectionString', 'sqlite:///:memory:')

    config.add_section('SSH')
    config.set('SSH', 'Password', 'pass')
    config.set('SSH', 'Username', 'user')
    config.set('SSH', 'PortToForward', '3306')
    config.set('SSH', 'Address', '127.0.0.1')
    config.set('SSH', 'Enable', 'true')

    with open('config.cfg', 'w') as configfile:
        config.write(configfile)

    print('Please fill out config.cfg, then restart the program.')
    exit(1)

ser = serial.Serial(config.get('Serial', 'Port'),
                    config.getint('Serial', 'Baud'))

# Database Setup
# for debugging
# engine = create_engine('sqlite:///:memory:', echo=True)
# for production
engine = create_engine(config.get('Database', 'ConnectionString'))
Base = declarative_base()


class Member(Base):
    __tablename__ = 'members'

    mid = Column(String(length=40), primary_key=True)
    name = Column(String(length=100))
    # picture = Column(LargeBinary)


class CheckIn(Base):
    __tablename__ = 'checkin'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    mid = Column(String(length=40), ForeignKey("members.mid"), nullable=False)
    timeIn = Column(DateTime)
    timeOut = Column(DateTime)


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


class PhotoEntry:
    def __init__(self, master, id_num):
        self.id_num = id_num

        self.frame = Frame(master)
        self.frame.pack()

        self.instructions = Label(self.frame,
                                  text="Enter your name in the box, then click 'Take Photo.' The shutter will release 5 seconds after you click that button.")
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

        os.system('ffmpeg -f v4l2 -i /dev/video0 -video_size 1280x720 -vframes 1 images/%s.png -y' % str(self.id_num).replace("'", ''))

        img = PIL.Image.open("images/%s.png" % str(self.id_num).replace("'", ''))
        photo = PIL.ImageTk.PhotoImage(img)
        if self.picture is not None:
            self.picture.destroy()
        self.picture = Label(self.frame, image=photo)
        self.picture.image = photo
        self.picture.pack()
        self.img_string = img.tobytes()
        self.photo_button.config(state=NORMAL)
        self.instructions.config(
            text="If you are happy with the photo, click 'Submit Photo', otherwise take a new photo")

    def submit(self):
        if self.name is None or self.img_string is "":
            return

        session = Session()
        newMember = Member(mid=self.id_num, name=self.name)
        newLog = CheckIn(mid=self.id_num, timeIn=datetime.datetime.utcnow(), timeOut=None)
        session.add_all([newMember, newLog])
        session.commit()
        self.frame.quit()


class Login:
    def __init__(self, master, id_num):
        session = Session()
        frame = Frame(master)
        frame.pack()

        member = session.query(Member).filter_by(mid=id_num).first()

        topline = "%s\n[%s]" % (member.name, str(id_num))
        nameline = Label(frame, text=topline, bg="black", fg="white", font="Monospace 30")
        nameline.pack(fill=X)

        lastLog = session.query(CheckIn).filter_by(mid=id_num).filter_by(timeOut=None)

        if lastLog.count() == 0:
            statusline = Label(frame, text="CHECKED IN", bg="black", fg="green", font="Monospace 30")
            statusline.pack(fill=X)
            newLog = CheckIn(mid=id_num, timeIn=datetime.datetime.utcnow(), timeOut=None)
            session.add(newLog)

        else:
            lastLog = lastLog.first()
            statusline = Label(frame, text="CHECKED OUT", bg="black", fg="red", font="Monospace 30")
            statusline.pack(fill=X)
            lastLog.timeOut = datetime.datetime.utcnow()

        if os.path.isfile("images/%s.png" % str(id_num).replace("'", '')):
            img = PIL.Image.open("images/%s.png" % str(id_num).replace("'", ''))
            photo = PIL.ImageTk.PhotoImage(img)
            picture = Label(frame, image=photo)
            picture.image = photo
            picture.pack()

        session.commit()


def display_login(id_num):
    root = Tk()
    gui = Login(root, id_num)
    root.after(5000, lambda: root.destroy())
    root.mainloop()


def run_entry(id_num):
    root = Tk()
    gui = PhotoEntry(root, id_num)
    root.mainloop()
    root.destroy()


def run_loop():
    id_num = ser.readline().strip()
    print(id_num)
    if len(id_num) != 35:
        # TODO: log misread
        log.error("Line missized: ignoring")
        return
    if not prox.check_parity(id_num):
        # TODO: log parity failure
        log.error("Parity error: ignoring")
        return

    session = Session()
    memberExists = session.query(Member).filter(Member.mid == id_num).count() > 0

    if memberExists:
        # If the user exists, toggle their in lab status and display that to them
        display_login(id_num)
    else:
        # If they don't exist, prompt them to add themselves
        #      Field for name
        #      Display webcam
        #      On click (or something) take and display a picture to them
        #      After they approve it, store it somewhere, and make a new record for them
        #      Also, check them in
        run_entry(id_num)


while True:
    run_loop()