from komorasoft.app import db


class Sensor(db.Model):
    __tablename__ = 'senzorji'

    sid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    state = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"Senzor:    {self.name}, stanje:    {self.state}"
    
    def get_id(self):
        return self.sid