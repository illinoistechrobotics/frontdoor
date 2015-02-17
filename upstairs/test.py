import serial
import redis

#On the laptop, the Arduino enumerates as COM3
#I've specified the baud rate to be max (115200)

ser = serial.Serial("COM3", 115200) #I'm not going to specify a timeout so I can be blocking on the serial port
red = redis.Redis()

def check_parity(code):
    if len(code) is not 35:
        return False
    bool_code = [int(x) for x in list(code)]
    return full_parity(bool_code) and odd_parity(bool_code) and even_parity(bool_code)

def full_parity(code):
    a = 0
    for b in code:
        a += b
    return bool(a % 2)

def even_parity(code):
    a = 0
    for bit in [x-1 for x in [2,3,4,6,7,9,10,12,13,15,16,18,19,21,22,24,25,27,28,30,31,33,34]]:
        a += code[bit]
    return not bool(a % 2)

def odd_parity(code):
    a = 0
    for bit in [x-1 for x in [2,3,5,6,8,9,11,12,14,15,17,18,20,21,23,24,26,27,29,30,32,33,35]]:
        a += code[bit]
    return bool(a % 2)

def display_login(id_num, status):
    pass


def run_loop():
    line = ser.readline().strip()
    if len(line) != 35:
        #TODO: log misread
        return
    if check_parity(line) is not true:
        #TODO: log parity failure
        return
    #Check redis for the user with that id
    name = red.get(line+'.name')
    if name is not None:
        #If the user exists, toggle their in lab status and display that to them
        #Send an update hook to the itr website
        status = red.incr(line)
        display_checkin(line, status)
        pass
    else:
        #If they don't exist, prompt them to add themselves
        #      Field for name
        #      Display webcam
        #      On click (or something) take and display a picture to them
        #      After they approve it, store it somewhere, and make a new record for them
        #      Also, check them in
        pass
