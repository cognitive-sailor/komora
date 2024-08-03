from komorasoft.app import db
from sqlalchemy import UniqueConstraint


class Sensor(db.Model):
    __tablename__ = 'senzorji'

    sid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    state = db.Column(db.Boolean, nullable=False)
    description = db.Column(db.String)

    __table_args__ = (
        UniqueConstraint('name', name='uq_name'),
    )
    

    def __repr__(self):
        return f"{self.name}, stanje:    {self.state},    opis:    {self.description}"
    
    def get_id(self):
        return self.sid