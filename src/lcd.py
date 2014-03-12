#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import wiringPy
import time
import struct

from PIL import Image
#from pcd8544.font import default_FONT
#from pcd8544.util import flatten
from font import default_FONT
from util import flatten
import A20_GPIO as GPIO

# screen size in pixel
HEIGHT = WIDTH = 84

fd = -1 # FIXME bitbang file descriptor







# default PINs, BCM GPIO
pin_CLK   = GPIO.PIN2_6 # Orange
pin_DIN   = GPIO.PIN2_8 # Gelb
pin_DC    = GPIO.PIN2_10 # Grün
pin_CE    = GPIO.PIN2_12 # Blau
pin_LIGHT = GPIO.PIN2_14 # Weiß
pin_RST   = GPIO.PIN2_16 # Braun
 


# useful constants
ON,   OFF = [1, 0]
HIGH, LOW = [1, 0]

# contrast
default_contrast = 0xC0

def init(CLK = 11, DIN = 10, DC = 23, RST = 24, LIGHT = 18, CE = 8, contrast = default_contrast):
    """ init screen, clearscreen """
    #wiringPy.debug(0)

    #if wiringPy.setup_gpio() != 0:
    #   raise IOError("Failed to initialize wiringPy properly")

    #fd = wiringPy.setup_bitbang(CE, DIN, CLK, 0)
    #if fd == -1:
    #    raise IOError("Failed to initialize bitbang properly")
    GPIO.init()
    #pins = [CLK, DIN, DC, RST, LIGHT, CE]
    pins = [pin_CLK, pin_DIN, pin_DC, pin_RST, pin_LIGHT, pin_CE]
    #pin_CLK, pin_DIN, pin_DC, pin_RST, pin_LIGHT, pin_CE = pins
    for pin in pins:
        GPIO.setcfg(pin, GPIO.OUTPUT)
        GPIO.output(pin,GPIO.HIGH)
    #map(lambda p: , pins)
    # Reset the device
    GPIO.output(pin_RST, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(pin_RST, GPIO.HIGH)
    set_contrast(contrast)
    #command([0x26])
    cls()

def set_contrast(value):
    """ sets the LCD contrast """
    command([0x21, 0x14, value, 0x20, 0x0c])

def backlight(status):
    """ control backlight """
    #wiringPy.digital_write(pin_LIGHT, 1 - status)
    if status==0:
        GPIO.output(pin_LIGHT, GPIO.HIGH)
    else:
        GPIO.output(pin_LIGHT, GPIO.LOW)    

def command(arr):
    """ write commands """
    bitmap(arr, OFF)

def data(arr):
    """ write data """
    bitmap(arr, ON)

def bitmap(arr, dc):
    """ write a sequence of bytes, either as data or command"""    
    #wiringPy.digital_write(pin_DC, dc)
    #wiringPy.digital_write(pin_DC, dc)
    if dc==ON:
        GPIO.output(pin_DC, GPIO.HIGH)
    else:
        GPIO.output(pin_DC, GPIO.LOW)
    #str=struct.pack('B'*len(arr), *arr)
    #print(str)
    #print(arr);
    #for item in arr:
    #    writeonebyte(item)
    #wiringPy.digital_write_serial_array(0, )
    GPIO.bitbang(pin_CLK,pin_DIN,pin_CE,struct.pack('B'*len(arr), *arr))
def testBit(int_type, offset):
    mask = 1 << offset
    return(int_type & mask)
def writeonebyte(data):
    GPIO.output(pin_CE, GPIO.LOW)
    #data=bit_reverse(data)
    for i in range(0,8):
        if testBit(data,i)!=0:
            GPIO.output(pin_DIN, GPIO.HIGH)
            #print("1")
        else:
            GPIO.output(pin_DIN, GPIO.LOW)
            #print("0")
        GPIO.output(pin_CLK, GPIO.LOW)
        #time.sleep(0.01)
        GPIO.output(pin_CLK, GPIO.HIGH)
        
    GPIO.output(pin_CE, GPIO.HIGH)

def position(x, y):
    """ goto to column x in seg y """
    command([x + 0x80, y + 0x40])

def cls():
    """ clear screen """
    position(0, 0)
    data([0] * (HEIGHT * WIDTH / 8))
    position(0, 0)

def locate(x, y):
    """ goto (x,y) to paint a character """
    position(x * 6, y)

def text(string, font = default_FONT, align = 'left'):
    """ draw string at current position """
    map(lambda c: data(font[c] + [0x00]), string)

def smooth_hscroll(string, row, iterations, delay=0.2, font=default_FONT):
    """ scrolls string at given row """
    bytes = list(flatten(map(lambda c: font[c] + [0x00], string)))
    for i in xrange(iterations):
        position(0, row)
        data(bytes[i:i+84])
        time.sleep(delay)

def bit_reverse(value, width=8):
  result = 0
  for _ in xrange(width):
    result = (result << 1) | (value & 1)
    value >>= 1

  return result

BITREVERSE = map(bit_reverse, xrange(256))

def image(im, reverse=False):
    """ draw image """
    mask = 0xFF if reverse else 0x00
    # Rotate and mirror the image
    rim = im.rotate(-90).transpose(Image.FLIP_LEFT_RIGHT)
    command([0x22])  # Change display to vertical write mode for graphics
    position(0, 0)
    data([BITREVERSE[ord(x)] ^ mask for x in list(rim.tostring())])
    command([0x20])  # Switch back to horizontal write mode for text
