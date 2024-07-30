from komorasoft.app import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'uporabniki'

    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)
    description = db.Column(db.String)

    def __repr__(self):
        return f"Uporabnik:    {self.username},        vloga:    {self.role}"
    
    def get_id(self):
        return self.uid