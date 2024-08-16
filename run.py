from komorasoft.app import create_app
from flask_apscheduler import APScheduler
# from komorasoft.scripts.tests.test_functions import log_cpu_usage, log_ram_usage

flask_app = create_app()

scheduler = APScheduler()

if __name__ == '__main__':
    # # Test functions
    # scheduler.add_job(func=log_cpu_usage,trigger='interval',seconds=5, id='cpu_job')
    # scheduler.add_job(func=log_ram_usage,trigger='interval',seconds=10, id='ram_job')
    scheduler.start()
    flask_app.run(host='0.0.0.0', debug=False)