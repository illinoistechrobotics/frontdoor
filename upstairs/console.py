import math
import redis
import Adafruit_CharLCD as LCD


def read_card(bits):
    cardreader = open('/dev/prox','r')
    data = cardreader.read(math.ceil(bits/8.0))
    #bits can be unaligned, so we need to fix them
    bitstring = "{0:b}".format(data)
    bitstring = bitstring[len(bitstring) - bits:]
    return bitstring

def write_card_lcd(card_number, name, status):
    lcd.message(name + '\n' + status)


def lookup_card(card_number, redis):
    pipe =  redis.pipeline()
    status = ''
    if pipe.sismember("IN", card_number):
        pipe.srem("IN", card_number)
        status = 'OUT'
    else:
        pipe.sadd("IN", card_number)
        status = 'IN'
    pipe.execute()
    name = redis.get(card_number + "_name")
    return (name, status)

#open redis connection
while(1):
    bitstring = read_card(26)

