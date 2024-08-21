import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
# while True:
#     GPIO.setup(26, GPIO.IN)
#     a = GPIO.input(26)
#     if a:
#         print("prizgano")
#     else:
#         print("ugasnjeno")
#     time.sleep(0.1)
'''
14 = kompresor
15 = ventilator uparjalnik
18 = N2
23 = LED
24 = UV
25 = ventilator zrak
8 = valžilnik
7 = luč kamera
16 = /
12 = grelec uparjalnika
'''
# a = GPIO.setup(7,GPIO.OUT)
# GPIO.output(a,GPIO.LOW)
RELAYS = [14,15,18,23,24,25,8,7,16,12]
for pin in RELAYS:
    GPIO.setup(pin,GPIO.OUT)
    GPIO.output(pin,GPIO.HIGH)
    time.sleep(1)
    GPIO.output(pin,GPIO.LOW)
    # time.sleep(2)

