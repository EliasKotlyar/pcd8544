#!/usr/bin/env python

#import pcd8544.lcd as lcd
import lcd
import time
import A20_GPIO as GPIO

def demo():
    lcd.locate(0,0)
    lcd.text("TEST")        

if __name__ == "__main__":
    lcd.init()
    lcd.backlight(1)
    demo()
    GPIO.cleanup()

