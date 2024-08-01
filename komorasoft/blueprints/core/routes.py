from flask import render_template, Blueprint

from komorasoft.app import db

core = Blueprint('core', __name__, static_folder='static', template_folder='templates')

@core.route('/')
def index():
    return render_template('core/index.html')

@core.route('/not_authorized')
def not_authorized():
    return render_template('core/not_authorized.html')