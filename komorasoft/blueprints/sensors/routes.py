from flask import request, render_template, redirect, url_for, Blueprint
from flask_login import current_user, login_required

from komorasoft.app import db
from komorasoft.blueprints.sensors.models import Sensor

sensors = Blueprint('sensors', __name__, static_folder='static', template_folder='templates')

@sensors.route('/')
def index():
    sensors = Sensor.query.all()
    #cols = [column.name for column in Sensor.__table__.columns]
    cols = ["ID","Naziv","Stanje","Opis","Dejanja"]
    rows = [[sensor.sid,sensor.name,sensor.state,sensor.description] for sensor in sensors]
    return render_template('sensors/index.html', sensors=sensors, columns=cols, rows=rows)

@sensors.route('/create', methods=['GET','POST'])
@login_required
def create():
    if request.method == 'GET':
        return render_template('sensors/create.html')
    elif request.method == 'POST':
        name = request.form.get('naziv')
        desc = request.form.get('description')
        desc = desc if desc != '' else None # dodaj opis, če ga je uporabnik definiral
        state = False # preveri dejansko stanje senzorja!

        existing_sensors = Sensor.query.all() # get all sensors
        sensor_names = [sensor.name for sensor in existing_sensors] # get all sensor names

        if name not in sensor_names:
            sensor = Sensor(name=name, description=desc, state=state) # dodaj nov senzor

            db.session.add(sensor)
            db.session.commit()

            return redirect(url_for('sensors.index'))
        else:
            return render_template('sensors/sensor_exists.html')
    
@sensors.route('/delete', methods=['GET','POST'])
@login_required
def delete():
    if request.method == 'GET':
        sensors = Sensor.query.all()
        return render_template('sensors/delete.html', sensors=sensors)
    elif request.method == 'POST':
        name = request.form.get('naziv')

        sensor = Sensor.query.filter(Sensor.name == name).first()

        if current_user.is_authenticated:
            if current_user.role == "Administrator":
                db.session.delete(sensor)
                db.session.commit()
                return redirect(url_for('sensors.index'))
            else:
                return render_template('sensors/not_authorized.html')
        else:
            return render_template('sensors/not_authorized.html')
        

@sensors.route('/edit', methods=['GET','POST'])
@login_required
def edit():
    if request.method == 'GET':
        return render_template('sensors/edit.html')
    elif request.method == 'POST':
        name_old = request.form.get('name_old')
        name = request.form.get('name')
        desc = request.form.get('description')
        desc = desc if desc != '' else None # dodaj opis, če ga je uporabnik definiral
        state = False # preveri dejansko stanje aktuatorja!

        sensor = Sensor.query.filter(Sensor.name == name_old).first()

        if current_user.is_authenticated and current_user.role=="Administrator":
            sensor.name = name
            sensor.description = desc
            sensor.state = state
            db.session.commit()  # Commit the changes to the database
            return redirect(url_for('sensors.index'))
        else:
            return render_template('sensors/not_authorized.html')