from flask import request, render_template, redirect, url_for, Blueprint, jsonify
from flask_login import current_user, login_required

from komorasoft.app import db
from komorasoft.blueprints.actuators.models import Actuator
from komorasoft.blueprints.simple.models import Settings

manual = Blueprint('manual', __name__, static_folder='static', static_url_path='/static', template_folder='templates')


@manual.route('/')
@login_required
def index():
    active_setting = Settings.query.filter_by(active=True).first() # find active setting
    print(active_setting)
    if active_setting:
        print("test 1")
        return render_template('manual/setting_active.html')
    else:
        if current_user.role == "Administrator":
            print("test 2")
            actuators = Actuator.query.all()  # Fetch all actuators from the database
            return render_template('manual/index.html', actuators=actuators)
        else:
            return render_template('manual/not_authorized.html')
        

@manual.route('/toggle_device', methods=['POST'])
def toggle_device():
    data = request.get_json()
    device_id = data.get('device_id')
    if device_id is None:
        return jsonify({'error': 'No device_id provided'}), 400

    # Find the actuator by its ID
    actuator = Actuator.query.get(device_id)
    if actuator is None:
        return jsonify({'error': 'Actuator not found'}), 404

    # Toggle the state
    actuator.state = not actuator.state

    # Commit the changes to the database
    db.session.commit()

    # Return the new state as a response
    return jsonify({'new_state': actuator.state})
    
    