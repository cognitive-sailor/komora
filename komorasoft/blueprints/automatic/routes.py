from flask import request, jsonify, render_template, redirect, url_for, Blueprint
from flask_login import current_user, login_required
from komorasoft.app import db
from komorasoft.blueprints.auto.models import Schedule, ActuatorEvent
from komorasoft.blueprints.actuators.models import Actuator
from datetime import datetime, timedelta
from typing import List, Optional

automatic = Blueprint('automatic', __name__, static_folder='static', template_folder='templates/automatic')

@automatic.route('/')
def index():
    return render_template('index.html')