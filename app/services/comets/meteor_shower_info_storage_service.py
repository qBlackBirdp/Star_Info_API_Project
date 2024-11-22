# services/comets/meteor_shower_info_storage_service.py

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from app.models.meteor_shower_raw_data import MeteorShowerInfo
from app.services.comets.meteor_shower_info import get_meteor_shower_info
from app.data.data import METEOR_SHOWERS
from app.db.db_utils import get_session, retry_query
import atexit


def save_meteor_shower_info(session, shower_info):
    """
    유성우 정보를 데이터베이스에 저장하는 함수.

    Args:
        session: SQLAlchemy 세션.
        shower_info (dict): 저장할 유성우 정보.
    """
    peak_period_str = ', '.join(shower_info["peak_period"]) if isinstance(shower_info["peak_period"], list) else \
        shower_info["peak_period"]

    meteor_shower_record = MeteorShowerInfo(
        comet_name=shower_info["comet_name"],
        name=shower_info["name"],
        peak_period=peak_period_str,
        peak_start_date=shower_info["peak_start_date"],
        peak_end_date=shower_info["peak_end_date"],
        message=shower_info["message"],
        conditions_used=shower_info["conditions_used"],
        status=shower_info["status"],
        distance=shower_info["distance"],
        ra=shower_info["ra"],
        declination=shower_info["declination"]
    )
    session.add(meteor_shower_record)


def update_meteor_shower_data():
    """
    앞으로 3년간의 유성우 데이터를 모든 혜성에 대해 저장하는 함수.
    """
    comet_names = ["Halley", "Swift-Tuttle", "Tuttle"]
    current_year = datetime.now().year

    with get_session() as session:
        try:
            for comet_name in comet_names:
                for year_offset in range(3):  # 3년치 데이터를 가져오기 위해 반복
                    year = current_year + year_offset
                    start_date = f"{year}-01-01"
                    range_days = 365  # 1년씩 데이터 조회

                    # 유성우 정보 가져오기
                    shower_info_list = get_meteor_shower_info(comet_name, start_date, range_days)

                    if isinstance(shower_info_list, list):
                        for shower_info in shower_info_list:
                            # 중복 데이터 확인 후 저장
                            query = session.query(MeteorShowerInfo).filter(
                                MeteorShowerInfo.comet_name == shower_info["comet_name"],
                                MeteorShowerInfo.peak_start_date == datetime.strptime(
                                    shower_info["peak_start_date"], '%Y-%m-%d').date()
                            )

                            existing_info = retry_query(session, query)

                            if not existing_info:
                                save_meteor_shower_info(session, shower_info)

                        # 변경사항 커밋
                        session.commit()
                    else:
                        error_message = shower_info_list.get('error', "Unknown error")
                        print(f"Error updating data for {comet_name}: {error_message}")
                        raise Exception(f"Error updating data for {comet_name}: {error_message}")
        except Exception as e:
            session.rollback()
            print(f"Failed to update meteor shower data: {e}")


# 스케줄러 설정
scheduler = BackgroundScheduler()
# 3년마다 1월 1일 자정에 유성우 데이터를 업데이트하는 작업 추가
scheduler.add_job(update_meteor_shower_data, 'cron', year='*/3', month='1', day='1', hour='0', minute='0')
scheduler.start()

# 앱이 종료될 때 스케줄러도 같이 종료되도록 설정
atexit.register(lambda: scheduler.shutdown())


def get_stored_meteor_shower_info(comet_name, year=None):
    """
    저장된 유성우 정보를 반환하는 함수.

    Args:
        comet_name (str): 혜성의 이름.
        year (int, optional): 검색할 연도. None이면 모든 연도의 정보를 가져옴.

    Returns:
        list: 유성우 정보 리스트.
    """
    try:
        with get_session() as session:
            query = session.query(MeteorShowerInfo).filter(MeteorShowerInfo.comet_name == comet_name)

            if year:
                query = query.filter(MeteorShowerInfo.peak_start_date.between(f"{year}-01-01", f"{year}-12-31"))

            results = retry_query(session, query)

            if not results:
                return {"error": "No meteor shower info found for the specified comet."}

            return [
                {
                    "name": row.name,
                    "peak_period": row.peak_period,
                    "peak_start_date": row.peak_start_date.isoformat(),
                    "peak_end_date": row.peak_end_date.isoformat(),
                    "message": row.message,
                    "conditions_used": row.conditions_used,
                    "status": row.status,
                    "distance": row.distance,
                    "ra": row.ra,
                    "declination": row.declination
                }
                for row in results
            ]
    except Exception as e:
        return {"error": f"Database operation failed: {e}"}
