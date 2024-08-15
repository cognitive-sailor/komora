from flask import request, render_template, redirect, url_for, Blueprint, jsonify
from flask_login import current_user, login_required
import json
from datetime import datetime, timedelta

from komorasoft.app import db
from komorasoft.blueprints.simple.models import Settings, ActuatorSetting

simple = Blueprint('simple', __name__, static_folder="static", template_folder='templates/simple')


@simple.route('/')
@login_required
def index():
    if current_user.role == "Administrator":
        return render_template('index.html')
    else:
        return render_template('not_authorized.html')
    

@simple.route('/save_settings', methods=['POST'])
@login_required
def save_settings():

    # Function that check if a set interval is longer than a duration
    def checkIntervalVSDuration(actuator,intDays,intHours,intMinutes,intSeconds,DurHours,DurMinutes,DurSeconds):
        interval_length = timedelta(days=intDays,hours=intHours,minutes=intMinutes,seconds=intSeconds)
        duration_length = timedelta(hours=DurHours,minutes=DurMinutes,seconds=DurSeconds)
        print(f"Interval: {interval_length}, Duration: {duration_length}")
        return interval_length > duration_length, actuator
    
    # Function that inserts user inputs to the database for every actuator setting
    def settings2db(settings_obj, data, advanced, exists):
        if not exists:
            # Create new settings for every acutator
            for actuator, actuator_settings in data.items(): # for each actuator, read data for interval and duration
                usr_control = True if advanced else False
                if actuator not in ["settingsID","advancedCheck","settingsDescription","settingsTitle","temperatureRange"]:
                    intDays = actuator_settings[actuator+'IntDays']
                    intHours = actuator_settings[actuator+'IntHours']
                    intMinutes = actuator_settings[actuator+'IntMinutes']
                    intSeconds = actuator_settings[actuator+'IntSeconds']
                    DurHours = actuator_settings[actuator+'DurHours']
                    DurMinutes = actuator_settings[actuator+'DurMinutes']
                    DurSeconds = actuator_settings[actuator+'DurSeconds']

                    interval_shorter_than_dur, incorrect_actuator = checkIntervalVSDuration(actuator,intDays,intHours,intMinutes,intSeconds,DurHours,DurMinutes,DurSeconds)
                    if interval_shorter_than_dur:
                        newActuatorSetting = ActuatorSetting(name=actuator,
                                                            user_control=usr_control,
                                                            interval_days=intDays,
                                                            interval_hours=intHours,
                                                            interval_minutes=intMinutes,
                                                            interval_seconds=intSeconds,
                                                            duration_hours=DurHours,
                                                            duration_minutes=DurMinutes,
                                                            duration_seconds=DurSeconds,
                                                            settings_id=settings_obj.id)
                    
                        db.session.add(newActuatorSetting)
                        db.session.commit()
                    else:
                        return jsonify({'message': f'The interval is shorter than the duration at actuator setting: {incorrect_actuator}'})
        else:
            # Find and update the existing setting for every actuator
            for actuator, actuator_settings in data.items(): # for each actuator, read data for interval and duration
                usr_control = True if advanced else False
                if actuator not in ["settingsID","advancedCheck","settingsDescription","settingsTitle","temperatureRange"]:
                    print(f"Nastavitev: {actuator}")
                    editActuatorSetting = ActuatorSetting.query.filter_by(name=actuator, settings_id=settings_obj.id).first()
                    print(f"Stevilo act nastavitev {len(ActuatorSetting.query.filter_by(name=actuator, settings_id=settings_obj.id).all())}")
                    print(editActuatorSetting)
                    print(editActuatorSetting.id)

                    intDays = actuator_settings[actuator+'IntDays']
                    intHours = actuator_settings[actuator+'IntHours']
                    intMinutes = actuator_settings[actuator+'IntMinutes']
                    intSeconds = actuator_settings[actuator+'IntSeconds']
                    DurHours = actuator_settings[actuator+'DurHours']
                    DurMinutes = actuator_settings[actuator+'DurMinutes']
                    DurSeconds = actuator_settings[actuator+'DurSeconds']

                    interval_shorter_than_dur, incorrect_actuator = checkIntervalVSDuration(actuator,intDays,intHours,intMinutes,intSeconds,DurHours,DurMinutes,DurSeconds)
                    if interval_shorter_than_dur:
                        editActuatorSetting.user_control = usr_control
                        editActuatorSetting.interval_days = intDays
                        editActuatorSetting.interval_hours = intHours
                        editActuatorSetting.interval_minutes = intMinutes
                        editActuatorSetting.interval_seconds = intSeconds
                        editActuatorSetting.duration_hours = DurHours
                        editActuatorSetting.duration_minutes = DurMinutes
                        editActuatorSetting.duration_seconds = DurSeconds
                        editActuatorSetting.settings_id = settings_obj.id
                    
                        db.session.commit()
                    else:
                        return jsonify({'message': f'The interval is shorter than the duration at actuator setting: {incorrect_actuator}'})

    if current_user.role == "Administrator":
        data = request.json # get data from JS
        settingsID = data['settingsID']['settingsID'] # setting's ID
        name = data['settingsTitle']['settingsTitle'] # user defined or selected settings Title
        description = data['settingsDescription']['settingsDescription'] if data['settingsDescription']['settingsDescription'] != "" else "Brez opisa." # user defined or selected settings description
        temperature = data['temperatureRange']['temperatureRange'] # user defined temperature [Int]
        advanced = data['advancedCheck']['advancedCheck'] # check if user defined advanced settings [True/False]
        
        existingSettings = Settings.query.filter_by(id=settingsID).first()

        if existingSettings: # assign the new values = overwrite the Settings
            # Edit the Settings
            existingSettings.description = description # update description
            existingSettings.temperature = temperature # update temperature
            existingSettings.advanced = advanced # update advanced
            db.session.commit()
            # set the rest of the parameters
            settings2db(existingSettings, data, advanced, True)
            return jsonify(data)
        else:
            # Create new Settings
            newSettings = Settings(name=name,description=description,advanced=advanced,temperature=temperature)
            db.session.add(newSettings)
            db.session.commit()
            # set the rest of the parameters
            settings2db(newSettings, data, advanced, False)
            return jsonify(data), 201
    else:
        return render_template('not_authorized.html')
    


@simple.route('/get_settings', methods=['GET'])
def get_settings():
    settings = Settings.query.all()
    settings_data = [{'id': setting.id, 
                      'name': setting.name, 
                      'description':setting.description, 
                      'created':setting.created} for setting in settings]
    return jsonify(settings_data)

@simple.route('/get_setting/<string:setting_id>', methods=['GET'])
def get_setting(setting_id):
    # Fetch the setting from the database
    setting = Settings.query.get(setting_id)
    advanced = setting.advanced
    temperature = setting.temperature
    act_settings = setting.actuator_settings
    # act_setting = ActuatorSetting.query.filter_by(settings_id=setting_id).all()
    return_data = {} # prepare empty dictionary
    return_data['id'] = setting.id
    return_data['settingsTitle'] = setting.name
    return_data['settingsDescription'] = setting.description
    return_data['temperature'] = temperature
    return_data['advanced'] = advanced
    if act_settings:
        for act in act_settings:
            # Convert the setting to a dictionary
            return_data[act.name] = {
                "interval_days": act.interval_days,
                "interval_hours": act.interval_hours,
                "interval_minutes": act.interval_minutes,
                "interval_seconds": act.interval_seconds,
                "duration_hours": act.duration_hours,
                "duration_minutes": act.duration_minutes,
                "duration_seconds": act.duration_seconds,
                # Add other fields as necessary
            }
        return jsonify(return_data)
    else:
        # If the setting is not found, return an error response
        return jsonify({"error": "Setting not found"}), 404
    
@simple.route('/delete_setting', methods=['POST'])
@login_required
def delete_setting():
    if current_user.role == "Administrator":
        setting_id = request.form.get('deleteSettingId')
        settings2delete = Settings.query.get(setting_id)
        if settings2delete:
            db.session.delete(settings2delete)
            db.session.commit()
            return render_template('index.html')
        else:
            return jsonify({'message': f'No settings found with ID {setting_id}'}), 404
    else:
        return render_template('not_authorized.html')
    

@simple.route('/check_active_settings', methods=['GET'])
def check_active_settings():
    # Query the database for any active Settings
    active_settings = Settings.query.filter_by(active=True).first()
    
    # Return True if any active Settings exist, otherwise False
    if active_settings:
        return jsonify({'active': True, 'settingName':active_settings.name})
    else:
        return jsonify({'active': False})