from flask import request, render_template, redirect, url_for, Blueprint
from flask_login import current_user, login_required

from komorasoft.app import db
from komorasoft.blueprints.actuators.models import Actuator

simple = Blueprint('simple', __name__, static_folder="static", template_folder='templates/simple')


@simple.route('/')
@login_required
def index():
    if current_user.role == "Administrator":
        return render_template('index.html')
    else:
        return render_template('not_authorized.html')