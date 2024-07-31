from komorasoft.app import db


class Actuator(db.Model):
    __tablename__ = 'aktuatorji'

    sid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    state = db.Column(db.Boolean, nullable=False)
    description = db.Column(db.String)
    

    def __repr__(self):
        return f"{self.name}, stanje:    {self.state},   opis:    {self.description}"
    
    def get_id(self):
        return self.sid