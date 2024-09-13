import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
RELAYS = [14,15,18,23,24,25,8,7,12,16]
for pin in RELAYS:
    GPIO.setup(pin,GPIO.OUT)
    GPIO.output(pin,GPIO.LOW)
