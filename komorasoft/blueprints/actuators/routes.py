from flask import request, render_template, redirect, url_for, Blueprint
from flask_login import current_user

from komorasoft.app import db
from komorasoft.blueprints.actuators.models import Actuator

actuators = Blueprint('actuators', __name__, template_folder='templates')


@actuators.route('/')
def index():
    actuators = Actuator.query.all()
    #cols = [column.name for column in Actuator.__table__.columns]
    cols = ["ID","Naziv","Stanje","Opis","Dejanja"]
    rows = [[actuator.sid,actuator.name,actuator.state,actuator.description] for actuator in actuators]
    return render_template('actuators/index.html', actuators=actuators, columns=cols, rows=rows)

@actuators.route('/create', methods=['GET','POST'])
def create():
    if request.method == 'GET':
        return render_template('actuators/create.html')
    elif request.method == 'POST':
        name = request.form.get('naziv')
        desc = request.form.get('description')
        desc = desc if desc != '' else None # dodaj opis, če ga je uporabnik definiral
        state = False # preveri dejansko stanje aktuatorja!

        actuator = Actuator(name=name, description=desc, state=state) # dodaj nov aktuator

        db.session.add(actuator)
        db.session.commit()

        return redirect(url_for('actuators.index'))
    
@actuators.route('/delete', methods=['GET','POST'])
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
def edit():
    if request.method == 'GET':
        return render_template('actuators/edit.html')
    elif request.method == 'POST':
        name_old = request.form.get('name_old')
        name = request.form.get('name')
        desc = request.form.get('description')
        desc = desc if desc != '' else None # dodaj opis, če ga je uporabnik definiral
        state = False # preveri dejansko stanje aktuatorja!

        actuator = Actuator.query.filter(Actuator.name == name_old).first()

        if current_user.is_authenticated and current_user.role=="Administrator":
            actuator.name = name
            actuator.description = desc
            actuator.state = state
            db.session.commit()  # Commit the changes to the database
            return redirect(url_for('actuators.index'))
        else:
            return render_template('actuators/not_authorized.html')