from komorasoft.app import create_app
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import threading
import time
from flask_socketio import SocketIO
from sqlalchemy import event
from komorasoft.blueprints.simple.models import Settings
from komorasoft.scripts.main_control import switch_on, switch_off
from komorasoft.blueprints.actuators.models import Actuator
from datetime import timedelta, datetime
import cv2
import os
import h5py
import numpy as np
from filelock import FileLock
import socket
import pickle
from datetime import datetime

flask_app = create_app()

# Initialize the SocketIO instance
socketio = SocketIO(flask_app, logger=False, engineio_logger=False)

# Initialize the APScheduler instance
scheduler = BackgroundScheduler()
scheduler.start()

# # Set the lock on 
sensor_data = '/home/komora/KomoraMeritveSenzorjev/.sensor_data_app.h5'
# lock = FileLock(sensor_data + '.lock')

next_defrost_start_time = None
def temperature_control(id):
    global next_defrost_start_time
    pause_heating_interval = timedelta(minutes=15)
    heating_duration = timedelta(minutes=5)
    current_time = datetime.now()
    if next_defrost_start_time == None:
        next_defrost_start_time = current_time + pause_heating_interval
    # Check if it is time to start defrosting => turn on the heater
    if current_time >= next_defrost_start_time and current_time < (next_defrost_start_time+heating_duration):
        print("=========================================================")
        print("defrost in action")
        print("=========================================================")

        switch_off(1) # kompresor OFF
        switch_on(2) # ventilator uparjalnika ON
        switch_on(9) # grelec uparjalnika ON
        if (next_defrost_start_time+heating_duration-timedelta(seconds=5)) < current_time and current_time <= (next_defrost_start_time+heating_duration):
            # update defrost start time for the next cycle
            next_defrost_start_time = current_time + pause_heating_interval
            print("=========================================================")
            print("defrosting ended!")
            print("=========================================================")

    else:
        switch_off(9) # grelec uparjalnika OFF
        # Read sensor temperatures from HDF5 file
        sensor_temp = temp_indicator()
        # with lock:
        #     with h5py.File(sensor_data, 'r') as f:
        #         all_temps = f['experiment/temperatures/Temperature']
        #         temps = all_temps[-1,[1,2]] # get the latest T2 and T3
        #         sensor_temp = np.average(temps)
        #         socketio.emit('update_temp', {'temp': sensor_temp})
        #         # Get user specified temperature
        with flask_app.app_context():
            setting = Settings.query.get(id)
            set_temp = int(setting.temperature)
            if sensor_temp > set_temp:
                # Turn on the AC cooling
                switch_on(1) # kompresor ON
                switch_on(2) # ventilator uparjalnika ON
            else:
                switch_off(1) # kompresor OFF
                switch_off(2) # ventilator uparjalnika OFF


def camera_read():
    save_path = "/mnt/shramba/"+datetime.now().strftime("%Y-%m-%d")
    cam = cv2.VideoCapture(0) # setup a camera
    result, image = cam.read()
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    cv2.imwrite(save_path+"/"+datetime.now().isoformat()+".jpg", image)
    print("Image caputred!")

def actuator_control(id,duration):
    switch_on(id) # turn ON the physical actuator
    print(f"Actuator {id}: ON (auto control)")
    if id == 8:
        switch_on(4) # turn ON the LED
        switch_on(7) # turn ON the camera ring light
        time.sleep(0.5)
        camera_read() # take a photo
        switch_off(4) # turn OFF the LED
        switch_off(7) # turn OFF the camera ring light
    time.sleep(duration)
    switch_off(id) # turn OFF the physical actuator and wait for the interval to end
    print(f"Actuator {id}: OFF (auto control)")


last_active_setting = ""
@event.listens_for(Settings,'after_update')
def update_indicators(mapper, connection, target):
    global last_active_setting
    with flask_app.app_context():
        # Update the indicators in the app
        if target.active:
            socketio.emit('update_status', {'active': target.active, 'active_name': target.name})
            # Write job start time to HDF5 sensor_data.h5 file
            # Setup socket client that sends active/inactive setting trigger to the sensors_read.py
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 54492))  # Connect to the server on localhost
            client_socket.settimeout(7.0)
            data = pickle.dumps([target.active,target.name])
            # client_socket.sendall(str(data).encode('utf-8'))  # Send data to the server
            client_socket.sendall(data)
            client_socket.close()
            last_active_setting = target.name
            # with lock:
            #     with h5py.File(sensor_data, 'a') as f:
            #         jobs_ds = f['experiment/job runs/jobs']
            #         print("=========================================")
            #         print(jobs_ds.shape)
            #         jobs_ds.resize((jobs_ds.shape[0]+1, jobs_ds.shape[1])) # make space for new entry
            #         print(jobs_ds.shape)
            #         jobs_ds[-1,0] = np.bytes_(datetime.now().isoformat()) # write start time
            #         f.flush()
            # Start temperature control
            scheduler.add_job(func=temperature_control,args=[target.id],trigger=IntervalTrigger(seconds=2),id='temperature_control_job')
            # Actuators control
            actuators = Actuator.query.all()
            for act in actuators:
                print(act.name, act.interval, act.duration)
                if not (act.interval == act.duration == timedelta(seconds=0)):
                    print(f"Automatic control: {act.name} every {act.interval}s for {act.duration}s")
                    existing_job = scheduler.get_job(str(act.id))
                    if existing_job:
                        print(f"Job {act.name} is running")
                    else:
                        # Create a new job
                        scheduler.add_job(func=actuator_control,
                                        args=[act.id,int(act.duration.total_seconds())],
                                        trigger=IntervalTrigger(seconds=int(act.interval.total_seconds())),
                                        id=str(act.id))
                        print(f"Job {act.name} created!")
        # elif not target.active:
            # with lock:
            #     with h5py.File(sensor_data, 'a') as f:
            #         jobs_ds = f['experiment/job runs/jobs']
            #         jobs_ds.resize((jobs_ds.shape[0]+1, jobs_ds.shape[1])) # make space for new entry
            #         jobs_ds[-1,1] = np.bytes_(datetime.now().isoformat()) # write end time
            #         f.flush()
        else:
            socketio.emit('update_status', {'active': False, 'active_name': ""})
            existing_temp_job = scheduler.get_job('temp_indicator_job')
            if existing_temp_job:
                print("Job temp indicator already running.")
            else:
                scheduler.add_job(func=temp_indicator,trigger='interval',seconds=5,id='temp_indicator_job')
            if target.name == last_active_setting:
                # Write job end time to HDF5 sensor_data.h5 file
                # Setup socket client that sends active/inactive setting trigger to the sensors_read.py
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect(('localhost', 54492))  # Connect to the server on localhost
                client_socket.settimeout(7.0)
                data = pickle.dumps([target.active,target.name])
                # client_socket.sendall(str(data).encode('utf-8'))  # Send data to the server
                client_socket.sendall(data)
                client_socket.close()
                print("Job end time sent to sensors_read.py!")
                last_active_setting = ""



@event.listens_for(Actuator,'after_update')
def receive_after_update(mapper, connection, target):
    with flask_app.app_context():
        socketio.emit('toggle_actuators',{'data':target.is_active})
        active_setting = Settings.query.filter_by(active=True).first()
        if active_setting:
            print("automatic SIMPLE control")
        else:
            scheduler.remove_all_jobs()
            scheduler.add_job(func=temp_indicator,trigger='interval',seconds=5,id='temp_indicator_job')
            # print("manual control ########################### ")
            if target.is_active:
                switch_on(target.id) # turn ON physical device
                print(f"Manual control, {target.name} switched ON")
                if target.id == 8:
                    camera_read()
                    time.sleep(0.5)
                    switch_off(target.id)
            else:
                switch_off(target.id) # turn OFF physical device
                print(f"Manual control, {target.name} switched OFF")
            

def temp_indicator():
    # Read sensor temperatures from HDF5 file
    # with lock:
    with h5py.File(sensor_data, 'r') as f:
        all_temps = f['experiment/temperatures/Temperature']
        temps = all_temps[-1,[0,2]] # get the latest T2 and T3
        sensor_temp = np.average(temps)
    
        # Update temperature indicator
        with flask_app.app_context():
            socketio.emit('update_temp', {'temp': sensor_temp})        
    return sensor_temp

scheduler.add_job(func=temp_indicator,trigger='interval',seconds=5,id='temp_indicator_job')


# Start Flask-SocketIO server
if __name__ == '__main__':
    socketio.run(flask_app, host='0.0.0.0', debug=True)
    # run_main_control()
