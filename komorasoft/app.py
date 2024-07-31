from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt


db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./blueprints.db'

    app.secret_key = 'some key'

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    from komorasoft.blueprints.users.models import User
    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(uid)
    
    bcrypt = Bcrypt(app)

    from komorasoft.blueprints.users.routes import register_user_routes

    register_user_routes(app, db, bcrypt)

    # import and register all blueprints
    from komorasoft.blueprints.sensors.routes import sensors # import sensors blueprint
    from komorasoft.blueprints.actuators.routes import actuators
    from komorasoft.blueprints.core.routes import core
    from komorasoft.blueprints.users.routes import users

    app.register_blueprint(core, url_prefix='/')
    app.register_blueprint(users, url_prefix='/users')
    app.register_blueprint(sensors, url_prefix='/sensors')
    app.register_blueprint(actuators, url_prefix='/actuators')


    migrate = Migrate(app, db)

    return app