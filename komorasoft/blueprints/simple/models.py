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
    interval_days = db.Column(db.Integer, nullable=False, default=0)
    interval_hours = db.Column(db.Integer, nullable=False, default=0)
    interval_minutes = db.Column(db.Integer, nullable=False, default=0)
    interval_seconds = db.Column(db.Integer, nullable=False, default=0)
    duration_hours = db.Column(db.Integer, nullable=False, default=0)
    duration_minutes = db.Column(db.Integer, nullable=False, default=0)
    duration_seconds = db.Column(db.Integer, nullable=False, default=0)
    settings_id = db.Column(db.String, db.ForeignKey('settings.id'), nullable=False)

    def __repr__(self) -> str:
        return f"{self.name} ActuatorSetting: active every = {self.interval_days} d, {self.interval_hours} h, {self.interval_minutes} min, {self.interval_seconds} s,\n, for the duration of = {self.duration_hours} h, {self.duration_minutes} min, {self.duration_seconds} s.\n Belongs to {self.settings_id}"

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

