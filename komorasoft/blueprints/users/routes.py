from flask import request, render_template, redirect, url_for, Blueprint

from komorasoft.app import db
from komorasoft.blueprints.users.models import User

from flask_login import login_user, logout_user, current_user, login_required

users = Blueprint('users', __name__, template_folder='templates')


def register_routes(app, db, bcrypt):
    @users.route('/')
    def index():
        users = User.query.all()
        if current_user.is_authenticated:
            return render_template('users/index.html', users=users, current_user=current_user)
        else:
            return render_template('users/index.html', users=users, current_user=None)


    @users.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'GET':
            return render_template('users/signup.html')
        elif request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            role = request.form.get('role')
            desc = request.form.get('description')
            desc = desc if desc != '' else None # dodaj opis, če ga je uporabnik definiral

            hashed_password = bcrypt.generate_password_hash(password)

            user = User(username=username, password=hashed_password, role=role, description=desc) # dodaj novega uporabnika

            db.session.add(user)
            db.session.commit()
            return redirect(url_for('users.index'))


    @users.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('users/login.html')
        elif request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            user = User.query.filter(User.username == username).first()

            if bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('users.index'))
            else:
                return 'Neuspešen vpis'
            
    @users.route('/delete', methods=['GET', 'POST'])
    @login_required
    def delete():
        if request.method == 'GET':
            users = User.query.all()
            return render_template('users/delete.html', users=users)
        elif request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            user = User.query.filter(User.username == username).first()

            if bcrypt.check_password_hash(user.password, password) and current_user.role == "Administrator":
                db.session.delete(user)
                db.session.commit()
                return redirect(url_for('users.index'))
            else:
                return 'Izbris uporabnika neuspešen.'

    @users.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('core.index'))
    