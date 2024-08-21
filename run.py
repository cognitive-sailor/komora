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
from datetime import timedelta

flask_app = create_app()

# Initialize the SocketIO instance
socketio = SocketIO(flask_app, logger=False, engineio_logger=False)

# Initialize the APScheduler instance
scheduler = BackgroundScheduler()
scheduler.start()

def actuator_control(id,duration):
    # from komorasoft.app import db
    # actuator = Actuator.query.get(id)
    # actuator.is_active = True # set the "is_active" state of actuator to True in the database
    # db.session.commit()
    switch_on(id) # turn ON the physical actuator
    print(f"Actuator {id}: ON (auto control)")
    time.sleep(duration)
    switch_off(id) # turn OFF the physical actuator and wait for the interval to end
    print(f"Actuator {id}: OFF (auto control)")
    # actuator.is_active = False # set the "is_active" state of actuator to True in the database
    # db.session.commit()


@event.listens_for(Settings,'after_update')
def update_indicators(mapper, connection, target):
    with flask_app.app_context():
        # Update the indicators in the app
        if target.active:
            socketio.emit('update_status', {'active': target.active, 'active_name': target.name})

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
        else:
            socketio.emit('update_status', {'active': False, 'active_name': ""})



@event.listens_for(Actuator,'after_update')
def receive_after_update(mapper, connection, target):
    with flask_app.app_context():
        socketio.emit('toggle_actuators',{'data':target.is_active})
        active_setting = Settings.query.filter_by(active=True).first()
        if active_setting:
            print("automatic SIMPLE control")
        else:
            scheduler.remove_all_jobs()
            # print("manual control ########################### ")
            if target.is_active:
                switch_on(target.id) # turn ON physical device
                print(f"Manual control, {target.name} switched ON")
            else:
                switch_off(target.id) # turn OFF physical device
                print(f"Manual control, {target.name} switched OFF")
            

# scheduler.add_job(func=active_setting_start_jobs,trigger='interval',seconds=5,id='active_setting_start_jobs_job')


# Start Flask-SocketIO server
if __name__ == '__main__':
    socketio.run(flask_app, host='0.0.0.0', debug=True)
    # run_main_control()
