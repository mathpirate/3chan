from flask_sqlalchemy import SQLAlchemy
from threechan.heroku_app import app
db = SQLAlchemy(app)

class Allocation(db.Model):
    __tablename__ = "allocations"
    id = db.Column(db.Integer, primary_key=True)
    participant_number = db.Column(db.String)
    front_number = db.Column(db.String)
    admin_number = db.Column(db.String)

    def __init__(self, p, f, a):
        self.participant_number = p
        self.front_number = f
        self.admin_number = a

    def __repr__(self):
        return 'P: %s, F: %s, A: %s' % (self.participant_number, self.front_number, self.admin_number)
