from database import db

class Votes(db.Model):
    __tablename__ = "votes"
    song_id = db.Column(db.String(), primary_key=True, nullable=False)
    jammer = db.Column(db.Integer)
    not_jammer = db.Column(db.Integer)