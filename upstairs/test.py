import serial
import redis
import logging
import time
from VideoCapture import Device

log = logging.getLogger(__name__)
#On the laptop, the Arduino enumerates as COM3
#I've specified the baud rate to be max (115200)

ser = serial.Serial("COM3", 115200) #I'm not going to specify a timeout so I can be blocking on the serial port
cam = Device()
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

def display_login(id_num, name, status):
			output = name+ ' [' +id_num+ '] '
	if status % 2:
		output += "Checkin"
		
	else:
		output += "Checkout"
	print(ouput)
	log.info(output)

def run_loop():
    line = ser.readline().strip()
    if len(line) != 35:
        #TODO: log misread
		log.error("Line missized: ignoring")
        return
    if check_parity(line) is not true:
        #TODO: log parity failure
		log.error("Parity error: ignoring")
        return
    #Check redis for the user with that id
    name = red.get(line+'.name')
    if name is not None:
        #If the user exists, toggle their in lab status and display that to them
        #Send an update hook to the itr website
        status = red.incr(line)
        display_checkin(line, name, status)
        pass
    else:
        #If they don't exist, prompt them to add themselves
        #      Field for name
        #      Display webcam
        #      On click (or something) take and display a picture to them
        #      After they approve it, store it somewhere, and make a new record for them
        #      Also, check them in
		name = input("What is your name?")
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
		
		
		
        pass
