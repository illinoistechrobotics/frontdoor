import math
import Adafruit_CharLCD as LCD

def read_card(bits):
    cardreader = open('/dev/prox','r')
    data = cardreader.read(math.ceiling(bits/8.0))
    #bits can be unaligned, so we need to fix them
    pass
def write_card_lcd(card_number, name, status):
    #lcd.
    pass
def lookup_card(card_number):
    pass
