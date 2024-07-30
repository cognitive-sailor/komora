from flask import request, render_template, redirect, url_for, Blueprint

from komorasoft.app import db
from komorasoft.blueprints.actuators.models import Actuator

actuators = Blueprint('actuators', __name__, template_folder='templates')

@actuators.route('/')
def index():
    actuators = Actuator.query.all()
    return render_template('actuators/index.html', actuators=actuators)

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