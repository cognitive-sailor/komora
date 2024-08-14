from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# from komorasoft.blueprints.actuators.models import default_db
# from komorasoft.blueprints.auto.models import schedule_db


db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder='templates')
    # Configure SQLAlchemy with multiple databases
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./blueprints.db'  # Default database URI
    app.config['SQLALCHEMY_BINDS'] = {
        'schedule_db': 'sqlite:///schedule.db',  # Additional database URI
        'settings_db': 'sqlite:///settings.db'
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.secret_key = 'a7d14b1b2a7ce906887ff28c5b211e1d6933fa9e8215fa843e8dc6b2e639b92aff2a33b715a9c240a8894457fda82e5d09536235774316e577052ee4cda58a40'

    login_manager = LoginManager()
    login_manager.init_app(app)

    from komorasoft.blueprints.users.models import User
    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(uid)
    
    @login_manager.unauthorized_handler
    def unauthorized_callback():
        return redirect(url_for('core.not_authorized'))

    bcrypt = Bcrypt(app)

    from komorasoft.blueprints.users.routes import register_user_routes

    register_user_routes(app, db, bcrypt)

    # import and register all blueprints
    from komorasoft.blueprints.sensors.routes import sensors # import sensors blueprint
    from komorasoft.blueprints.actuators.routes import actuators
    from komorasoft.blueprints.core.routes import core
    from komorasoft.blueprints.users.routes import users
    from komorasoft.blueprints.manual.routes import manual
    # from komorasoft.blueprints.auto.routes import auto
    # from komorasoft.blueprints.automatic.routes import automatic
    from komorasoft.blueprints.simple.routes import simple

    app.register_blueprint(core, url_prefix='/')
    app.register_blueprint(users, url_prefix='/users')
    app.register_blueprint(sensors, url_prefix='/sensors')
    app.register_blueprint(actuators, url_prefix='/actuators')
    app.register_blueprint(manual, url_prefix='/manual')
    # app.register_blueprint(auto, url_prefix='/auto')
    # app.register_blueprint(automatic, url_prefix='/automatic')
    app.register_blueprint(simple,url_prefix='/simple')
    
    db.init_app(app)
    migrate = Migrate(app, db)
    with app.app_context():
        db.create_all()  # This will create tables in the default database
        
    return app