from sensors_read import *

def initialize_actuators():
    RELAYS = {"kompresor":21,
              "vent_uparjalnika":20,
              "N2":26,
              "LED":19,
              "UV":13,
              "vent_zrak":6,
              "vlazilnik":12,
              "luc_kamera":5,
              "grelec":18}
    print("Turning OFF devices:")
    for device, pin in RELAYS.items():
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(pin, GPIO.OUT) # set pin as output
        # GPIO.output(pin, GPIO.LOW) # turn the pin off
        print(f"--> Pin {pin} = {device}")

def main():
    print("Starting the main program.\n")
    # 0. Initialize all actuators, set their states to "off"
    initialize_actuators()

    # 1. Read the current value of every sensor
    sensors_current_values = sensors_read()

    # 2. 

if __name__ == "__main__":
    main()
