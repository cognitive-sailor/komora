from datetime import datetime, timedelta
from typing import List, Optional
import uuid
from komorasoft.app import db
from sqlalchemy import UniqueConstraint

class ActuatorEvent(db.Model):
    __bind_key__ = 'schedule_db'
    __tablename__ = 'actuator_events'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    actuator_name = db.Column(db.String, nullable=False)
    state = db.Column(db.Boolean, nullable=False)
    offset = db.Column(db.Interval, nullable=False)
    schedule_id = db.Column(db.String, db.ForeignKey('schedules.schedule_id'), nullable=False)

    __table_args__ = (
        UniqueConstraint('actuator_name', name='uq_actuator_name'),
    )

    def __repr__(self) -> str:
        return f"{self.actuator_name} ActuatorEvent: time = {self.offset}, state = {self.state}. Belongs to {self.schedule_id}"

class Schedule(db.Model):
    __bind_key__ = 'schedule_db'
    __tablename__ = 'schedules'
    schedule_id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    start_time = db.Column(db.DateTime, nullable=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    events = db.relationship('ActuatorEvent', backref='schedule', lazy=True, cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('name', name='uq_name'),
    )

    def __repr__(self) -> str:
        return f"{self.name} schedule with start time = {self.start_time}, created on = {self.created}, with {len(self.events)} events and ID = {self.schedule_id}"

