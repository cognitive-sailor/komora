from flask import request, render_template, redirect, url_for, Blueprint, jsonify
from flask_login import current_user, login_required
import json
from datetime import datetime, timedelta

from komorasoft.app import db
from komorasoft.blueprints.actuators.models import Actuator
from komorasoft.blueprints.simple.models import Settings, ActuatorSetting
from komorasoft.scripts.frontend.updateui import update_active_setting, check_active, stop_all
from komorasoft.scripts.main_control import main_control

simple = Blueprint('simple', __name__, static_folder="static", template_folder='templates/simple')


def serialize_actuator(actuator):
    return {
        'id': actuator.id,
        'name': actuator.name,
        'description': actuator.description,
        # Add other fields as needed
    }

@simple.route('/')
@login_required
def index():
    if current_user.role == "Administrator":
        actuators = Actuator.query.filter(~Actuator.name.in_(["Kompresor","Ventilator uparjalnika","Grelec uparjalnika","Vlažilnik"])).all() # get all user controlable actuators
        ser_actuators = [serialize_actuator(actuator) for actuator in actuators]
        ptc_actuators = Actuator.query.filter(Actuator.name.in_(["Ventilator uparjalnika","Grelec uparjalnika","Vlažilnik"])).all() # get all potencial user controlable actuators
        ser_ptc_actuators = [serialize_actuator(actuator) for actuator in ptc_actuators]
        return render_template('index.html', actuators=ser_actuators, ptc_actuators=ser_ptc_actuators)
    else:
        return render_template('not_authorized.html')
    

@simple.route('/save_settings', methods=['POST'])
@login_required
def save_settings():

    # Function that check if a set interval is longer than a duration
    def checkIntervalVSDuration(intDays,intHours,intMinutes,intSeconds,DurHours,DurMinutes,DurSeconds):
        interval_length = timedelta(days=int(intDays),hours=int(intHours),minutes=int(intMinutes),seconds=int(intSeconds))
        duration_length = timedelta(hours=int(DurHours),minutes=int(DurMinutes),seconds=int(DurSeconds))
        print(f"Interval: {interval_length}, Duration: {duration_length}, Comparrison: {interval_length >= duration_length}")
        return interval_length, duration_length
    
    # Function that inserts user inputs to the database for every actuator setting
    def settings2db(settings_obj, data, advanced, exists):
        if not exists:
            # Create new settings for every acutator
            for actuator, actuator_settings in data.items(): # for each actuator, read data for interval and duration
                usr_control = True if advanced else False
                if actuator not in ["settingsID","advancedCheck","settingsDescription","settingsTitle","temperatureRange"]:
                    IntDays = actuator_settings[actuator+'IntDays']
                    IntHours = actuator_settings[actuator+'IntHours']
                    IntMinutes = actuator_settings[actuator+'IntMinutes']
                    IntSeconds = actuator_settings[actuator+'IntSeconds']
                    DurHours = actuator_settings[actuator+'DurHours']
                    DurMinutes = actuator_settings[actuator+'DurMinutes']
                    DurSeconds = actuator_settings[actuator+'DurSeconds']

                    interval_length, duration_length = checkIntervalVSDuration(IntDays,IntHours,IntMinutes,IntSeconds,DurHours,DurMinutes,DurSeconds)
                    if (interval_length > duration_length) or (interval_length == duration_length == timedelta(seconds=0)):
                        newActuatorSetting = ActuatorSetting(name=actuator,
                                                            user_control=usr_control,
                                                            IntDays=IntDays,
                                                            IntHours=IntHours,
                                                            IntMinutes=IntMinutes,
                                                            IntSeconds=IntSeconds,
                                                            DurHours=DurHours,
                                                            DurMinutes=DurMinutes,
                                                            DurSeconds=DurSeconds,
                                                            settings_id=settings_obj.id)
                        print("test 2.1")
                        db.session.add(newActuatorSetting)
                        db.session.commit()
                        print("test 2.2")
                        print(f"Created. Added the acutator's settings: {actuator, usr_control,IntDays,IntHours,IntMinutes,IntSeconds,settings_obj.id}")
                    else:
                        print(f'The interval is shorter than the duration at actuator setting: {actuator}')
                        return jsonify({'message': f'The interval is shorter than the duration at {actuator} setting'})
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

                    IntDays = actuator_settings[actuator+'IntDays']
                    IntHours = actuator_settings[actuator+'IntHours']
                    IntMinutes = actuator_settings[actuator+'IntMinutes']
                    IntSeconds = actuator_settings[actuator+'IntSeconds']
                    DurHours = actuator_settings[actuator+'DurHours']
                    DurMinutes = actuator_settings[actuator+'DurMinutes']
                    DurSeconds = actuator_settings[actuator+'DurSeconds']

                    interval_length, duration_length = checkIntervalVSDuration(IntDays,IntHours,IntMinutes,IntSeconds,DurHours,DurMinutes,DurSeconds)
                    if (interval_length > duration_length) or (interval_length == duration_length == timedelta(seconds=0)):
                        editActuatorSetting.user_control = usr_control
                        editActuatorSetting.IntDays = IntDays
                        editActuatorSetting.IntHours = IntHours
                        editActuatorSetting.IntMinutes = IntMinutes
                        editActuatorSetting.IntSeconds = IntSeconds
                        editActuatorSetting.DurHours = DurHours
                        editActuatorSetting.DurMinutes = DurMinutes
                        editActuatorSetting.DurSeconds = DurSeconds
                        editActuatorSetting.settings_id = settings_obj.id
                    
                        db.session.commit()
                        print(f"Edited. Changed the acutator's settings: {actuator, usr_control,IntDays,IntHours,IntMinutes,IntSeconds,settings_obj.id}")
                    else:
                        return jsonify({'message': f'The interval is shorter than the duration at actuator setting: {actuator}'})

    if current_user.role == "Administrator":
        data = request.json # get data from JS
        settingsID = data['settingsID']['settingsID'] # setting's ID
        name = data['settingsTitle']['settingsTitle'] # user defined or selected settings Title
        description = data['settingsDescription']['settingsDescription'] if data['settingsDescription']['settingsDescription'] != "" else "Brez opisa." # user defined or selected settings description
        temperature = data['temperatureRange']['temperatureRange'] # user defined temperature [Int]
        advanced = data['advancedCheck']['advancedCheck'] # check if user defined advanced settings [True/False]
        
        existingSettings = Settings.query.filter_by(id=settingsID, name=name).first()
        print(f"Submitted data: {data}")
        if existingSettings: # assign the new values = overwrite the Settings
            print(f"Editing. Name: {name}")
            # Edit the Settings
            existingSettings.description = description # update description
            existingSettings.temperature = temperature # update temperature
            existingSettings.advanced = advanced # update advanced
            db.session.commit()
            # set the rest of the parameters
            settings2db(existingSettings, data, advanced, True)
            return jsonify("Edited settings",data), 201
        else:
            print(f"Creating. Name: {name}, ID: {settingsID}")
            # Create new Settings
            newSettings = Settings(name=name,description=description,advanced=advanced,temperature=temperature)
            db.session.add(newSettings)
            db.session.commit()
            # set the rest of the parameters
            settings2db(newSettings, data, advanced, False)
            return jsonify("Created new settings",data), 201
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
    return_data['optionals'] = ["Ventilator uparjalnika","Grelec uparjalnika","Vlažilnik"]
    if act_settings:
        for act in act_settings:
            # Convert the setting to a dictionary
            return_data[act.name] = {
                "IntDays": act.IntDays,
                "IntHours": act.IntHours,
                "IntMinutes": act.IntMinutes,
                "IntSeconds": act.IntSeconds,
                "DurHours": act.DurHours,
                "DurMinutes": act.DurMinutes,
                "DurSeconds": act.DurSeconds,
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
            return redirect(url_for('simple.index'))
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
    


@simple.route('/start', methods=['GET','POST'])
@login_required
def start():

    def setting2Actuator(act_name,data):
        print(f"setting2Actuator:\nActuator: {act_name}, data: {data}")
        actuator = Actuator.query.filter_by(name=act_name) # get the actuator
        actuator.interval = timedelta(days=int(data['IntDays']),hours=int(data['IntHours']),minutes=int(data['IntMinutes']),seconds=int(data['IntSeconds']))
        actuator.duration = timedelta(hours=int(data['DurHours']),minutes=int(data['DurMinutes']),seconds=int(data['DurSeconds']))
        db.session.commit()


    if current_user.role == "Administrator":
        settingID = request.form.get('confirmStart_SettingID') # get ID of the setting the user is starting..
        update_active_setting(settingID) # set this setting to active, others to inactive
        currently_active_setting = check_active()

        # prepare all data for the main_control script
        data = get_setting(settingID).get_json() # get the submitted setting and strip it of HTTP to get only JSON
        optionals = data['optionals']
        # set interval and duration for every actuator in the database
        for actuator_setting in data.items():
            print(actuator_setting[0]) ####################################################################################################################
            if actuator_setting[0] not in ["id","settingsTitle","settingsDescription","temperature","advanced","optionals"]:
                setting2Actuator(actuator_setting[0],actuator_setting[1])
        # main_control(data) # send setting's data to the main control function

        return redirect(url_for('simple.index'))
    else:
        return render_template('not_authorized.html')

@simple.route('/stop', methods=['GET','POST'])
@login_required
def stop():
    if current_user.role == "Administrator":
        stop_all() # set all settings's active attribute to False
        message = "Zaustavili ste izvajanje programa!"
        return redirect(url_for('simple.index'))
    else:
        return render_template('not_authorized.html')