from komorasoft.app import db


class Actuator(db.Model):
    __tablename__ = 'aktuatorji'

    sid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    state = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"Aktuator:    {self.name}, stanje:    {self.state}"
    
    def get_id(self):
        return self.sid