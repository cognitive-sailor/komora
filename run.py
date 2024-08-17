# from komorasoft.app import create_app
# from flask_apscheduler import APScheduler
# import threading
# import atexit
# import time
# from flask_socketio import SocketIO, emit
# from komorasoft.blueprints.simple.models import Settings, ActuatorSetting

# from komorasoft.scripts.sensors_read import sensors_read
# # from komorasoft.scripts.tests.test_functions import log_cpu_usage, log_ram_usage

# flask_app = create_app()

# # ================  JOB SCHEDULER   ================

# scheduler = APScheduler()

# # Function to check if the job is running
# def ensure_job_is_running(job_name, job_function, seconds):
#     job = scheduler.get_job(job_name)
#     if not job:
#         print(f"Job {job_name} is not running. Restarting the job.")
#         scheduler.add_job(id=job_name, func=job_function, trigger='interval', seconds=seconds)

# def job_monitor(job_name, job_function, seconds):
#     while True:
#         ensure_job_is_running(job_name,job_function,seconds)
#         time.sleep(30)


# monitor_thread = threading.Thread(target=job_monitor,args=('Belezenje_senzorjev',sensors_read,10,))
# monitor_thread.start()

# # Register a function to be called when the program is exiting
# atexit.register(lambda: scheduler.shutdown())

# # ================/  JOB SCHEDULER   /================

# if __name__ == '__main__':
#     # # Test functions
#     # scheduler.add_job(func=log_cpu_usage,trigger='interval',seconds=5, id='cpu_job')
#     # scheduler.add_job(func=log_ram_usage,trigger='interval',seconds=10, id='ram_job')
#     scheduler.start()
#     flask_app.run(host='0.0.0.0', debug=False)








from komorasoft.app import create_app
from flask_apscheduler import APScheduler
import threading
import time
from flask_socketio import SocketIO
from komorasoft.blueprints.simple.models import Settings
from komorasoft.scripts.sensors_read import sensors_read

flask_app = create_app()

# Initialize the SocketIO instance
socketio = SocketIO(flask_app, cors_allowed_origins="*")

# Initialize the APScheduler instance
scheduler = APScheduler()

# Function to ensure the job is running
def ensure_job_is_running(job_name, job_function, seconds):
    job = scheduler.get_job(job_name)
    if not job:
        print(f"Job {job_name} is not running. Restarting the job.")
        scheduler.add_job(id=job_name, func=job_function, trigger='interval', seconds=seconds)

def job_monitor(job_name, job_function, seconds):
    while True:
        ensure_job_is_running(job_name, job_function, seconds)
        time.sleep(30)

# Define the job function
def update_indicators():
    with flask_app.app_context():  # Ensure app context is available
        active_setting = Settings.query.filter_by(active=True).first()  # Find active setting
        if active_setting:
            # Emit an event to all connected clients
            socketio.emit('update_status', {'active': active_setting.active, 'active_name': active_setting.name})
        else:
            socketio.emit('update_status', {'active': False, 'active_name': ""})

# Initialize and start the scheduler
scheduler.add_job(func=update_indicators, trigger='interval', seconds=5, id='update_indicators_job')
scheduler.start()

# Start a monitoring thread to ensure job is running
monitor_thread = threading.Thread(target=job_monitor, args=('Belezenje_senzorjev', sensors_read, 10,))
# monitor_thread.start()

# Start Flask-SocketIO server
if __name__ == '__main__':
    socketio.run(flask_app, host='0.0.0.0', debug=False)
