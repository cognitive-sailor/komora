from komorasoft.app import db
from komorasoft.blueprints.simple.models import Settings, ActuatorSetting
from komorasoft.blueprints.actuators.models import Actuator
from flask import jsonify
from datetime import timedelta
from komorasoft.scripts.main_control import switch_on, switch_off

def check_active():
    # Check if any and which setting is currently active
    active_setting = Settings.query.filter_by(active=True).first()
    return active_setting.name if active_setting else None
    
def update_active_setting(setting_id):
    # Get all settings from the database and set their active attribute to False
    existingSettings = Settings.query.all()
    for setting in existingSettings:
        setting.active = setting.id == setting_id # True only for sumbitted setting, all other: settings.active = False
    db.session.commit()

def stop_all():
    actuators = Actuator.query.all()
    for actuator in actuators:
        actuator.is_active = False
        actuator.interval = timedelta(seconds=0)
        actuator.duration = timedelta(seconds=0)
    db.session.commit()

def stop_all_settings():
    settings = Settings.query.all()
    for setting in settings:
        setting.active = False
    db.session.commit()