from flask import request, render_template, redirect, url_for, Blueprint
from flask_login import current_user, login_required

from komorasoft.app import db
from komorasoft.blueprints.actuators.models import Actuator

actuators = Blueprint('actuators', __name__, static_folder='static', template_folder='templates')


@actuators.route('/')
def index():
    actuators = Actuator.query.all()
    #cols = [column.name for column in Actuator.__table__.columns]
    cols = ["ID","Naziv","Stanje","Opis","Dejanja"]
    rows = [[actuator.id,actuator.name,actuator.is_active,actuator.description] for actuator in actuators]
    return render_template('actuators/index.html', actuators=actuators, columns=cols, rows=rows)

@actuators.route('/create', methods=['GET','POST'])
@login_required
def create():
    if request.method == 'GET':
        return render_template('actuators/create.html')
    elif request.method == 'POST':
        name = request.form.get('naziv')
        desc = request.form.get('description')
        desc = desc if desc != '' else None # dodaj opis, če ga je uporabnik definiral
        is_active = False # preveri dejansko stanje aktuatorja!

        existing_actuators = Actuator.query.all() # get all sensors
        actuator_names = [actuator.name for actuator in existing_actuators] # get all sensor names

        if name not in actuator_names:
            actuator = Actuator(name=name, description=desc, is_active=is_active) # dodaj nov aktuator

            db.session.add(actuator)
            db.session.commit()

            return redirect(url_for('actuators.index'))
        else:
            return render_template('actuators/actuator_exists.html')
    
@actuators.route('/delete', methods=['GET','POST'])
@login_required
def delete():
    if request.method == 'GET':
        actuators = Actuator.query.all()
        return render_template('actuators/delete.html', actuators=actuators)
    elif request.method == 'POST':
        name = request.form.get('naziv')

        actuator = Actuator.query.filter(Actuator.name == name).first()

        if current_user.is_authenticated and current_user.role == "Administrator":
            db.session.delete(actuator)
            db.session.commit()
            return redirect(url_for('actuators.index'))
        else:
            return render_template('actuators/not_authorized.html')
        

@actuators.route('/edit', methods=['GET','POST'])
@login_required
def edit():
    if request.method == 'GET':
        return render_template('actuators/edit.html')
    elif request.method == 'POST':
        name_old = request.form.get('name_old')
        name = request.form.get('name')
        desc = request.form.get('description')
        desc = desc if desc != '' else None # dodaj opis, če ga je uporabnik definiral
        is_active = False # preveri dejansko stanje aktuatorja!

        actuator = Actuator.query.filter(Actuator.name == name_old).first()

        if current_user.is_authenticated and current_user.role=="Administrator":
            actuator.name = name
            actuator.description = desc
            actuator.is_active = is_active
            db.session.commit()  # Commit the changes to the database
            return redirect(url_for('actuators.index'))
        else:
            return render_template('actuators/not_authorized.html')