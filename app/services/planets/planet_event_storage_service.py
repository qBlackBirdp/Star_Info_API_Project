# services/planet/planet_event_storage_service.py

from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from app.services.horizons_service import get_planet_position_from_horizons
from app.models.planet_raw_data import get_planet_raw_data_model
from sqlalchemy import Table, Column, Integer, String, Float, Date, MetaData, inspect
from app import db

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def create_yearly_table(year):
    table_name = f'planet_raw_data_{year}'
    metadata = MetaData()
    inspector = inspect(db.engine)

    if not inspector.has_table(table_name):
        new_table = Table(
            table_name,
            metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('planet_name', String(50), nullable=False),
            Column('reg_date', Date, nullable=False),
            Column('distance', Float, nullable=False),
            Column('s_o_t', Float, nullable=False)
        )
        metadata.create_all(db.engine)


def update_raw_data():
    """
    모든 행성에 대해 현재 연도와 다음 연도의 대접근 이벤트 데이터를 업데이트하는 함수
    """
    planets = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    current_year = datetime.now().year + 2

    try:
        for planet in planets:
            # 모든 행성에 대해 현재 연도와 다음 연도의 대접근 이벤트를 업데이트
            years_to_update = [current_year, current_year + 1]

            for year in years_to_update:

                # 테이블이 없으면 생성
                create_yearly_table(year)
                logging.info(f"Updating raw data for {planet} for the year {year}")

                # Horizons API를 사용해 해당 연도의 데이터 가져오기
                year_start_date = datetime(year, 1, 1)
                year_end_date = datetime(year, 12, 31)
                planet_data = get_planet_position_from_horizons(planet, year_start_date,
                                                                (year_end_date - year_start_date).days)

                if 'error' in planet_data:
                    logging.error(
                        f"Failed to retrieve planet data from Horizons API for {planet}: {planet_data['error']}")
                    continue

                horizons_data = planet_data.get('data')
                if not horizons_data:
                    logging.error(f"No valid data from Horizons API for {planet} in year {year}.")
                    continue

                # ORM 객체를 사용해 데이터를 삽입
                PlanetRawDataYear = get_planet_raw_data_model(year)
                for day_data in horizons_data:
                    reg_date = datetime.strptime(day_data["time"], '%Y-%b-%d %H:%M')

                    # ORM 객체를 사용해 데이터를 삽입
                    new_data = PlanetRawDataYear(
                        planet_name=planet,
                        reg_date=reg_date,
                        distance=float(day_data.get('delta')),
                        s_o_t=float(day_data.get('s-o-t'))
                    )
                    db.session.add(new_data)

                # 변경사항 커밋
                db.session.commit()

    except Exception as e:
        logging.error(f"Failed to update raw data: {e}")
        db.session.rollback()


# 스케줄링 설정
scheduler = BackgroundScheduler()
scheduler.add_job(update_raw_data, 'cron', month='1', day='1', hour='0', minute='0')
scheduler.start()
