from komorasoft.app import db
from sqlalchemy import UniqueConstraint
from datetime import datetime, timedelta
import asyncio
import logging


class Actuator(db.Model):
    __tablename__ = 'aktuatorji'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    interval = db.Column(db.Interval, default=timedelta(seconds=0), nullable=False)
    duration = db.Column(db.Interval, default=timedelta(seconds=0), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    last_activation_time = db.Column(db.DateTime, nullable=True)
    last_deactivation_time = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint('name', name='uq_name'),
    )
    

    def __repr__(self):
        return f"{self.name}, stanje:    {self.is_active},   opis:    {self.description}"
    
    def get_id(self):
        return self.id
    
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



async def control_actuator(actuator):
    now = datetime.now()
    
    try:
        # Calculate activation and deactivation times
        next_activation_time = actuator.last_activation_time + actuator.interval if actuator.last_activation_time else now + actuator.interval
        next_deactivation_time = actuator.last_activation_time + actuator.duration if actuator.last_activation_time else next_activation_time + actuator.duration

        # Activation logic
        if now >= next_activation_time and not actuator.is_active:
            logger.info(f"Activating {actuator.name} at {now}")
            actuator.is_active = True
            actuator.last_activation_time = now
            db.session.commit()

        # Deactivation logic
        if now >= next_deactivation_time and actuator.is_active:
            logger.info(f"Deactivating {actuator.name} at {now}")
            actuator.is_active = False
            actuator.last_deactivation_time = now
            db.session.commit()

    except Exception as e:
        logger.error(f"Error in controlling actuator {actuator.name}: {e}")
        db.session.rollback()  # Rollback the transaction on error
        # Implement retry logic if necessary
        