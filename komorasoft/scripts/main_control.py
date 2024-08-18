from datetime import datetime, timedelta
from komorasoft.blueprints.actuators.models import Actuator


def main_control(data):
    print("--------------------     Starting the main control function     --------------------")
    # 0. Append the timestamp of the execution:START to the submitted setting
    data['execution_start'] = datetime.now().strftime("%Y-%m-%d@%H:%M:%S")
    print(data)
    for actuator, settings in data.items():
        if actuator not in ["id","settingsTitle","settingsDescription","temperature","advanced","execution_start"]:
            # Dictionary
            interval = timedelta(days=settings["IntDays"],hours=settings["IntHours"],minutes=settings["IntMinutes"],seconds=settings["IntSeconds"])
            duration = timedelta(hours=settings["DurHours"],minutes=settings["DurMinutes"],seconds=settings["DurSeconds"])
            Actuator.query.filter_by(name=actuator)


