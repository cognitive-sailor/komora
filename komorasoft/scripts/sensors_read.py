"""Functions for data acquisition from various sensors
"""
import time
from datetime import datetime
# import board
# import adafruit_sht31d
# import busio
# import adafruit_scd4x
# import RPi.GPIO as GPIO
# import serial


def sensors_read() -> list:
    # T1, H1, T2, H2 = temp_humi_read()
    # CO2, T3, H3 = co2_temp_humi_read()
    # H2, _, O2 = h2o2_read()
    # return [T1,T2,T3,H1,H2,H3,CO2,H2,O2]
    print(f"Reading from sensors... {datetime.now()}")
    time.sleep(2)

def sensors_show():
    print("Reading from sensors:\n(1-2) SHT31-D (2x) [Temp, Humidity Sensor]\n(3) SCD41 [CO2, Temp, Humidity Sensor]\n(4) MQ-8 [Hydrogen Gas Sensor]\n(5) ME2-O2-fi20 [O2 Gas Sensor]")
    while True:
        temp_humi_read(disp=True)
        co2_temp_humi_read(disp=True)
        h2o2_read(disp=True)


def temp_humi_read(disp=False):
    # Create I2C bus and sensor objects
    i2c = board.I2C()  # uses board.SCL and board.SDA
    sensor1 = adafruit_sht31d.SHT31D(i2c, address=0x44)
    sensor2 = adafruit_sht31d.SHT31D(i2c, address=0x45)

    def read_sensor(sensor, name):
        try:
            temperature = sensor.temperature
            humidity = sensor.relative_humidity
            print(f"{name} - Temperature: {temperature:.2f} C, Humidity: {humidity:.2f} %")
        except RuntimeError as e:
            print(f"Error reading {name}: {e}")
    if disp:
        read_sensor(sensor1, "TH1")
        read_sensor(sensor2, "TH2")
    else:
        return sensor1.temperature, sensor1.relative_humidity, sensor2.temperature, sensor2.relative_humidity


def co2_temp_humi_read(disp=False):
    # Initialize the I2C bus
    i2c = busio.I2C(board.SCL, board.SDA)

    # Create the SCD4X object
    scd4x = adafruit_scd4x.SCD4X(i2c, address=0x62)

    scd4x.stop_periodic_measurement() # Ensure periodic measurement is stopped
    scd4x.measure_single_shot()

    if disp:
        print(f"CO2: {scd4x.CO2} ppm")
        print(f"Temperature: {scd4x.temperature} °C")
        print(f"Humidity: {scd4x.relative_humidity} %")
    else:
        return scd4x.CO2, scd4x.temperature, scd4x.relative_humidity

def h2o2_read(disp=False):
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=None)
    ser.reset_input_buffer()
    time.sleep(1)
    data = ser.readline().decode('utf-8').rstrip()
    if data:
        if disp:
            print(f"H2, O2, O2con: {data}")
        else:
            # Convert from string to float
            H2, O2, O2con = [float(number) for number in data.split()]
            return H2, O2, O2con
    else:
        print("No data recieved! [for H2 and O2 sensors]")



if __name__ == "__main__":
    sensors_read()
