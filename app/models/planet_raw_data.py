# models/planet_raw_data.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Date
from app import db

Base = declarative_base()


class PlanetRawData(db.Model):
    __tablename__ = 'planet_raw_data'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    planet_name = db.Column(db.String(50), nullable=False)
    reg_date = db.Column(db.Date, nullable=False)
    distance = db.Column(db.Float, nullable=False)
    s_o_t = db.Column(db.Float, nullable=False)


def get_planet_raw_data_model(year):
    """
    연도에 따라 동적으로 테이블을 매핑하는 함수
    """

    class PlanetRawDataYear(Base):
        __tablename__ = f'planet_raw_data_{year}'
        __table_args__ = {'extend_existing': True}

        id = Column(Integer, primary_key=True, autoincrement=True)
        planet_name = Column(String(50), nullable=False)
        reg_date = Column(Date, nullable=False)
        distance = Column(Float, nullable=False)
        s_o_t = Column(Float, nullable=False)

    return PlanetRawDataYear
