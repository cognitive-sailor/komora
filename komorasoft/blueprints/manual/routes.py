from flask import request, render_template, redirect, url_for, Blueprint
from flask_login import current_user, login_required

from komorasoft.app import db
from komorasoft.blueprints.actuators.models import Actuator

manual = Blueprint('manual', __name__, template_folder='templates')


@manual.route('/')
def index():
    return 'Hello'