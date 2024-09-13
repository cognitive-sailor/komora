from datetime import datetime, timedelta
from komorasoft.blueprints.actuators.models import Actuator
import RPi.GPIO as GPIO
import time


# def main_control(data):
#     print("--------------------     Starting the main control function     --------------------")
#     # 0. Append the timestamp of the execution:START to the submitted setting
#     data['execution_start'] = datetime.now().strftime("%Y-%m-%d@%H:%M:%S")
#     print(data)
#     for actuator, settings in data.items():
#         if actuator not in ["id","settingsTitle","settingsDescription","temperature","advanced","execution_start"]:
#             # Dictionary
#             interval = timedelta(days=settings["IntDays"],hours=settings["IntHours"],minutes=settings["IntMinutes"],seconds=settings["IntSeconds"])
#             duration = timedelta(hours=settings["DurHours"],minutes=settings["DurMinutes"],seconds=settings["DurSeconds"])
#             Actuator.query.filter_by(name=actuator)

def switch_on(actuator):
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
    GPIO.setmode(GPIO.BCM)
    actuator = str(actuator)
    RELAYS = {'1':15,'2':14,'3':18,'4':23,'5':24,'6':25,'7':8,'8':7,'9':12,'10':16}
    GPIO.setup(RELAYS[actuator],GPIO.OUT)
    GPIO.output(RELAYS[actuator],GPIO.HIGH)
    time.sleep(0.2)

def switch_off(actuator):
    GPIO.setmode(GPIO.BCM)
    actuator = str(actuator)
    RELAYS = {'1':15,'2':14,'3':18,'4':23,'5':24,'6':25,'7':8,'8':7,'9':12,'10':16}
    GPIO.setup(RELAYS[actuator],GPIO.OUT)
    GPIO.output(RELAYS[actuator],GPIO.LOW)
    time.sleep(0.2)


