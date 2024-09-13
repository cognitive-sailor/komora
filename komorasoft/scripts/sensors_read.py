"""Functions for data acquisition from various sensors
"""
from datetime import datetime
import time
import board
import adafruit_sht31d
import busio
import adafruit_scd4x
import RPi.GPIO as GPIO
import serial
import cv2
import h5py
import numpy as np


def sensors_show():
    print("Reading from sensors:\n(1-2) SHT31-D (2x) [Temp, Humidity Sensor]\n(3) SCD41 [CO2, Temp, Humidity Sensor]\n(4) MQ-8 [Hydrogen Gas Sensor]\n(5) ME2-O2-fi20 [O2 Gas Sensor]\n(6) DS18B20 temperature sensors T4, T5")
    # Initialize the I2C bus
    i2c = busio.I2C(board.SCL, board.SDA)

    arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1) # initialize arduino
    time.sleep(2)

    # Create the SCD4X object
    scd4x = adafruit_scd4x.SCD4X(i2c, address=0x62)
    while True:
        start_time = time.time()
        temp_humi_read(disp=True)
        co2_temp_humi_read(scd4x,disp=True)
        h2o2_read(arduino,disp=True)
        print(f"Script execution time: {time.time()-start_time}s")

def sensors_read():
    print("Reading from sensors:\n(1-2) SHT31-D (2x) [Temp, Humidity Sensor]\n(3) SCD41 [CO2, Temp, Humidity Sensor]\n(4) MQ-8 [Hydrogen Gas Sensor]\n(5) ME2-O2-fi20 [O2 Gas Sensor]\n(6) DS18B20 temperature sensors T4, T5")
    
    # 0. SENSORS INITIALIZATION

    i2c = busio.I2C(board.SCL, board.SDA) # configure i2c communication protocol
    arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1) # initialize arduino
    time.sleep(2) # wait for arduino to init
    scd4x = adafruit_scd4x.SCD4X(i2c, address=0x62) # Create the SCD4X object
    print("Sensors initialized.")

    # 1. FILE SETUP - where sensor data is stored
    file_name = '/home/komora/KomoraMeritveSenzorjev/sensor_data.h5'
    # 2. START THE FILE OPERATIONS AND ENTER THE MAIN LOOP
    with h5py.File(file_name, 'a') as f:
        # set/check folder (group) structure within a file
        exp_grp = f.require_group('experiment')
        temp_grp = exp_grp.require_group('temperatures')
        hum_grp = exp_grp.require_group('humidity')
        gas_grp = exp_grp.require_group('gas')
        job_grp = exp_grp.require_group('job runs')

        # set/check datasets within each group
        time_ds = exp_grp.require_dataset(name='Timestamps',
                                          shape=(0,),
                                          maxshape=(None,),
                                          dtype=h5py.string_dtype(),
                                          chunks=True)
        temp_ds = temp_grp.require_dataset(name='Temperature',
                                         shape=(0,5), # start with 0 rows with 5 different sensors
                                         maxshape=(None,5), # unlimited rows
                                         dtype=np.float64,
                                         chunks=True)
        hum_ds = hum_grp.require_dataset(name='Humidity',
                                         shape=(0,3), # start with 0 rows with 3 different sensors
                                         maxshape=(None,3), # unlimited rows
                                         dtype=np.float64,
                                         chunks=True)
        gas_ds = gas_grp.require_dataset(name='Gas',
                                         shape=(0,3), # start with 0 rows with 3 different sensors
                                         maxshape=(None,3), # unlimited rows
                                         dtype=np.float64,
                                         chunks=True)
        jobs_ds = job_grp.require_dataset(name='jobs',
                                          shape=(0,2),
                                          maxshape=(None,2),
                                          dtype=h5py.string_dtype(),
                                          chunks=True)
        # assing attributes to groups and datasets
        if 'units' not in temp_ds.attrs:
            temp_ds.attrs['units'] = 'Celsius'
        if 'description' not in temp_ds.attrs:
            temp_ds.attrs['description'] = 'Temperature readings. T1: outside the chamber. T2: inside the chamber in the box on the top. T3: bottom of the chamber. T4: up, on the cables. T5: up between the fins of the evaporator.'
        if 'units' not in hum_ds.attrs:
            hum_ds.attrs['units'] = '%'
        if 'description' not in hum_ds.attrs:
            hum_ds.attrs['description'] = 'Humidity readings - relative humidity. H1: outside the chamber. H2: inside the chamber in the box on the top. H3: bottom of the chamber.'
        if 'units' not in gas_ds.attrs:
            gas_ds.attrs['units'] = 'CO2:ppm, H2:ppm, O2:%'
        if 'description' not in gas_ds.attrs:
            gas_ds.attrs['description'] = 'Gasses in the chamber. Carbon dioxide: bottom of the chamber. Oxygen: box on the top of the chamber. Hydrogen: box on the top of the chamber.'
        if 'description' not in jobs_ds.attrs:
            jobs_ds.attrs['description'] = 'Start and stop times of each job run.'

        print("HDF5 file ready for action!")
        try:
            while True:
                # Read sensors
                current_time = np.bytes_(datetime.now().isoformat())
                T1, H1, T2, H2 = temp_humi_read(disp=False)
                # print("T1,T2,H1,H2 acquired")
                CO2, T3, H3 = co2_temp_humi_read(scd4x,disp=False)
                # print("CO2,T3,H3 acquired")
                try:
                    Hydrogen, Oxygen, T4, T5 = h2o2_read(arduino,disp=False)
                    # print("H2,O2,T4,T5 acquired")
                except:
                    Hydrogen = 0
                    Oxygen = 0
                    T4 = -500
                    T5 = -500
                    print("exception: H2,O2,T4,T5 not acquired")
                #print(f"Ti: {T1}, T2: {T2}, T3: {T3}, T4: {T4}, T5: {T5}\nH1: {H1}, H2: {H2}, H3: {H3}\nCO2: {CO2}, Hydrogen: {Hydrogen}, Oxygen: {Oxygen}")
                
                # Resize datasets to make room for new data
                time_ds.resize(time_ds.shape[0]+1, axis=0)
                temp_ds.resize(temp_ds.shape[0]+1, axis=0)
                hum_ds.resize(hum_ds.shape[0]+1, axis=0)
                gas_ds.resize(gas_ds.shape[0]+1, axis=0)

                # Append new data to hdf5 file
                time_ds[-1] = current_time
                temp_ds[-1,:] = [T1, T2, T3, T4, T5]
                hum_ds[-1,:] = [H1, H2, H3]
                gas_ds[-1,:] = [CO2, Hydrogen, Oxygen]

                # Flush changes to disk
                f.flush()

        except KeyboardInterrupt:
            print("Terminating reading sensors and closing the .h5 file.")
        

        

def temp_humi_read(disp=False):
    # Create I2C bus and sensor objects
    i2c = board.I2C()  # uses board.SCL and board.SDA
    sensor1 = adafruit_sht31d.SHT31D(i2c, address=0x44) # notranji senzor zgoraj
    sensor2 = adafruit_sht31d.SHT31D(i2c, address=0x45) # zunanji senzor

    def read_sensor(sensor, name):
        try:
            temperature = sensor.temperature
            humidity = sensor.relative_humidity
            print(f"T{name}: {temperature:.2f} ˚C, H{name}: {humidity:.2f} %")
        except RuntimeError as e:
            print(f"Error reading {name}: {e}")
    if disp:
        read_sensor(sensor1, "1")
        read_sensor(sensor2, "2")
    else:
        return sensor1.temperature, sensor1.relative_humidity, sensor2.temperature, sensor2.relative_humidity


def co2_temp_humi_read(scd4x,disp=False):
    # # Initialize the I2C bus
    # i2c = busio.I2C(board.SCL, board.SDA)

    # # Create the SCD4X object
    # scd4x = adafruit_scd4x.SCD4X(i2c, address=0x62)

    # scd4x.stop_periodic_measurement() # Ensure periodic measurement is stopped
    scd4x.measure_single_shot()

    if disp:
        print(f"CO2: {scd4x.CO2} ppm\nT3: {scd4x.temperature} °C, H3: {scd4x.relative_humidity} %")
    else:
        return scd4x.CO2, scd4x.temperature, scd4x.relative_humidity

def h2o2_read(arduino,disp=False):
    arduino.reset_input_buffer()
    data = arduino.readline().decode('utf-8').strip()
    # print(data)
    if data:
        # Convert from string to float
        H2con, O2con, T4, T5 = [float(number) for number in data.split()]
        if disp:
            print(f"H2con: {H2con}\nO2con: {O2con}\nT4: {T4}\nT5: {T5}")
        else:
            return H2con, O2con, T4, T5
    else:
        print("No data recieved! [for H2 and O2 sensors]")


def camera_read():
    cam = cv2.VideoCapture(0) # setup a camera
    result, image = cam.read()
    return image



if __name__ == "__main__":
    time.sleep(30)
    sensors_read()
