from flask import request, render_template, redirect, url_for, Blueprint, jsonify
from flask_login import current_user, login_required
import json

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
    

@simple.route('/import_settings', methods=['POST'])
@login_required
def import_settings():
    if current_user.role == "Administrator":
        if 'file' not in request.files:
            return 'No file part', 400
        
        file = request.files['file']
        
        if file.filename == '':
            return 'No selected file', 400
        
        if file:
            # Save the file (you can add your desired path here)
            file.save(f'komorasoft/data/settings/{file.filename}')
            return 'File successfully uploaded', 200
    else:
        return render_template('not_authorized.html')
    

@simple.route('/save_settings', methods=['POST'])
@login_required
def save_settings():


    # Function that inserts user inputs to the database for every actuator setting
    def settings2db(settings_obj, data, advanced):
        for actuator, actuator_settings in data.items(): # for each actuator, read data for interval and duration
                usr_control = True if advanced else False
                if actuator not in ["advancedCheck","settingsDescription","settingsTitle","temperatureRange"]:
                    intDays = actuator_settings[actuator+'IntDays']
                    intHours = actuator_settings[actuator+'IntHours']
                    intMinutes = actuator_settings[actuator+'IntMinutes']
                    intSeconds = actuator_settings[actuator+'IntSeconds']
                    DurHours = actuator_settings[actuator+'DurHours']
                    DurMinutes = actuator_settings[actuator+'DurMinutes']
                    DurSeconds = actuator_settings[actuator+'DurSeconds']

                    newActuatorSetting = ActuatorSetting(name=actuator,
                                                        user_control=usr_control,
                                                        interval_days=intDays,
                                                        interval_hours=intHours,
                                                        interval_minutes=intMinutes,
                                                        interval_seconds=intSeconds,
                                                        duration_hours=DurHours,
                                                        duration_minutes=DurMinutes,
                                                        duration_seconds=DurSeconds,
                                                        settings_id=newSettings.id)
                    db.session.add(newActuatorSetting)
                    db.session.commit()

    if current_user.role == "Administrator":
        data = request.json # get data from JS
        name = data['settingsTitle']['settingsTitle'] # user defined or selected settings Title
        description = data['settingsDescription']['settingsDescription'] # user defined or selected settings description
        temperature = data['temperatureRange']['temperatureRange'] # user defined temperature [Int]
        advanced = data['advancedCheck']['advancedCheck'] # check if user defined advanced settings [True/False]

        existingSettings = Settings.query.filter_by(name=name).first()

        if existingSettings: # assign the new values = overwrite the Settings
            # Edit the Settings
            existingSettings.temperature = temperature # update temperature
            existingSettings.advanced = advanced
            # set the rest of the parameters
            settings2db(existingSettings, data, advanced)
            return jsonify(data)
        else:
            # Create new Settings
            newSettings = Settings(name=name,description=description,advanced=advanced,temperature=temperature)
            db.session.add(newSettings)
            db.session.commit()
            # set the rest of the parameters
            settings2db(newSettings, data, advanced)
            return jsonify(data)
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