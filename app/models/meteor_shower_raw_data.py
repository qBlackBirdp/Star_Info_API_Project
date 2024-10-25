# models/meteor_shower_raw_data.py

from .. import db


class MeteorShowerInfo(db.Model):
    __tablename__ = 'meteor_shower_info'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comet_name = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    peak_period = db.Column(db.String(50), nullable=False)
    peak_start_date = db.Column(db.Date, nullable=False)
    peak_end_date = db.Column(db.Date, nullable=False)
    message = db.Column(db.String(255), nullable=False)
    conditions_used = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    distance = db.Column(db.String(50))
    ra = db.Column(db.String(50))
    declination = db.Column(db.String(50))

    def __repr__(self):
        return f"<MeteorShowerInfo {self.comet_name} - {self.name}>"
