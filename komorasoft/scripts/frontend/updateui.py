from komorasoft.app import db
from komorasoft.blueprints.simple.models import Settings, ActuatorSetting
from flask import jsonify

def check_active():
    # Check if any and which setting is currently active
    active_setting = Settings.query.filter_by(active=True).first()
    return active_setting.name
    
def update_active_setting(setting_id):
    # Get all settings from the database and set their active attribute to False
    existingSettings = Settings.query.all()
    for setting in existingSettings:
        setting.active = setting.id == setting_id # True only for sumbitted setting, all other: settings.active = False
        db.session.commit()

def stop_all():
    # Set all setting object's active attribute in the database to False
    existingSettings = Settings.query.all()
    for setting in existingSettings:
        setting.active = False
        db.session.commit()