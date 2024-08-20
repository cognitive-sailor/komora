from datetime import datetime, timedelta
import uuid
from komorasoft.app import db
from sqlalchemy import UniqueConstraint

class ActuatorSetting(db.Model):
    __bind_key__ = 'settings_db'
    __tablename__ = 'actuator_setting'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String, nullable=False)
    user_control = db.Column(db.Boolean, nullable=False, default=True)
    IntDays = db.Column(db.Integer, nullable=False, default=0)
    IntHours = db.Column(db.Integer, nullable=False, default=0)
    IntMinutes = db.Column(db.Integer, nullable=False, default=0)
    IntSeconds = db.Column(db.Integer, nullable=False, default=0)
    DurHours = db.Column(db.Integer, nullable=False, default=0)
    DurMinutes = db.Column(db.Integer, nullable=False, default=0)
    DurSeconds = db.Column(db.Integer, nullable=False, default=0)
    settings_id = db.Column(db.String, db.ForeignKey('settings.id'), nullable=False)

    def __repr__(self) -> str:
        return f"{self.name} ActuatorSetting: active every = {self.IntDays} d, {self.IntHours} h, {self.IntMinutes} min, {self.IntSeconds} s,\n, for the duration of = {self.DurHours} h, {self.DurMinutes} min, {self.DurSeconds} s.\n Belongs to {self.settings_id}"

class Settings(db.Model):
    __bind_key__ = 'settings_db'
    __tablename__ = 'settings'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, nullable=True)
    created = db.Column(db.DateTime, default=datetime.now())
    active = db.Column(db.Boolean, default=False, nullable=False)
    advanced = db.Column(db.Boolean, default=False, nullable=False)
    temperature = db.Column(db.Integer, nullable=False)
    actuator_settings = db.relationship('ActuatorSetting', backref='settings', lazy=True, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"{self.name} settings: active = {self.active}, advanced = {self.advanced}, created = {self.created}, opis = {self.description}."

