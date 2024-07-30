from flask import request, render_template, redirect, url_for, Blueprint

from komorasoft.app import db
from komorasoft.blueprints.sensors.models import Sensor

sensors = Blueprint('sensors', __name__, template_folder='templates')

@sensors.route('/')
def index():
    sensors = Sensor.query.all()
    return render_template('sensors/index.html', sensors=sensors)

@sensors.route('/create', methods=['GET','POST'])
def create():
    if request.method == 'GET':
        return render_template('sensors/create.html')
    elif request.method == 'POST':
        name = request.form.get('naziv')
        desc = request.form.get('description')
        desc = desc if desc != '' else None # dodaj opis, če ga je uporabnik definiral
        state = False # preveri dejansko stanje senzorja!

        sensor = Sensor(name=name, description=desc, state=state) # dodaj nov senzor

        db.session.add(sensor)
        db.session.commit()

        return redirect(url_for('sensors.index'))