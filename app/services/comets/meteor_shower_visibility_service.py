# services/comets/meteor_shower_visibility_service.py

from app.models.meteor_shower_raw_data import MeteorShowerInfo
from app import db
from datetime import datetime
from app.services.comets.commet_utils import calculate_altitude_azimuth  # 고도 계산에 사용할 유틸리티 함수
from app.services.directions_utils import azimuth_to_direction  # 동서남북 변환 함수 import
from app.services.moon_phase_service import get_moon_phase_for_date


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
            return []

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


def evaluate_meteor_shower_visibility(shower_name, year, latitude, longitude):
    try:
        # 유성우 데이터 조회
        meteor_shower_data = get_meteor_shower_data(shower_name, year)

        if isinstance(meteor_shower_data, dict) and "error" in meteor_shower_data:
            return meteor_shower_data

        if not meteor_shower_data:
            return {"error": "No meteor shower data found for the specified name and year."}

        visibility_results = []

        for data in meteor_shower_data:
            # 유성우의 적경(RA)과 적위(Dec)을 사용하여 고도와 방위각 계산
            ra = data["ra"]
            dec = data["declination"]
            peak_date = datetime.fromisoformat(data["peak_start_date"])
            elevation = 0  # 해수면 고도로 설정

            # 고도와 방위각 계산 (Skyfield 기반의 calculate_altitude_azimuth 함수 사용)
            altitude, azimuth = calculate_altitude_azimuth(ra, dec, data["distance"], latitude, longitude, elevation,
                                                           peak_date)

            # 방위각을 동서남북 방향으로 변환
            direction = azimuth_to_direction(azimuth)

            # 가시성 결과 초기화
            visibility_result = {
                "name": data["name"],
                "comet_name": data["comet_name"],
                "peak_period": data["peak_period"],
                "peak_dates": {
                    "start": data["peak_start_date"],
                    "end": data["peak_end_date"]
                },
                "message": data["message"],
                "conditions": {
                    "used": data["conditions_used"],
                    "status": data["status"]
                },
                "coordinates": {
                    "distance": data["distance"],
                    "ra": data["ra"],
                    "declination": data["declination"],
                    "latitude": latitude,
                    "longitude": longitude,
                    "altitude": altitude,
                    "direction": direction
                }
            }

            # 달의 위상 정보 추가
            moon_phase_info = get_moon_phase_for_date(peak_date)
            if "error" not in moon_phase_info:
                visibility_result.update(moon_phase_info)

            # 고도가 일정 기준 이상인 경우 가시성이 있는 것으로 판단
            if altitude > 15.0:  # 고도가 15도 이상이어야 관측 가능하다고 판단
                visibility_result["visibility_message"] = "Meteor shower is visible."
            else:
                visibility_result["visibility_message"] = "Altitude is too low for visibility."

            visibility_results.append(visibility_result)

        return {"visibility_results": visibility_results}

    except Exception as e:
        return {"error": f"Failed to evaluate meteor shower visibility: {e}"}
