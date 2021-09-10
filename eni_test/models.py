from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Topology(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Params = db.Column(db.String(50))
    ApNum = db.Column(db.Integer)
    EdgeNum = db.Column(db.Integer)
    ClientCount = db.Column(db.Integer)
    rechable = db.Column(db.String(50))
    UnrechableNum = db.Column(db.Integer)

    def __repr__(self):
        return '<id {}>'.format(self.id)