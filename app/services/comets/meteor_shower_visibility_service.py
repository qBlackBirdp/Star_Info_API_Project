# services/comets/meteor_shower_visibility_service.py

from app.models.meteor_shower_raw_data import MeteorShowerInfo
from app import db


def get_meteor_shower_data(shower_name, year):
    """
    특정 유성우 이름과 연도를 기준으로 데이터를 조회하는 함수

    Args:
        shower_name (str): 유성우의 이름.
        year (int): 조회할 연도.

    Returns:
        list: 유성우 정보 리스트 또는 에러 메시지.
    """
    try:
        query = db.session.query(MeteorShowerInfo).filter(
            MeteorShowerInfo.name == shower_name,
            MeteorShowerInfo.peak_start_date.between(f"{year}-01-01", f"{year}-12-31")
        )
        results = query.all()

        if not results:
            return {"error": "No meteor shower data found for the specified name and year."}

        # 조회된 데이터를 리스트로 반환
        return [
            {
                "name": row.name,
                "comet_name": row.comet_name,
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
