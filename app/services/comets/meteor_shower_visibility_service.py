# services/comets/meteor_shower_visibility_service.py

from app.models.meteor_shower_raw_data import MeteorShowerInfo
from datetime import datetime, timedelta
from app.services.comets.commet_utils import calculate_altitude_azimuth  # 고도 계산에 사용할 유틸리티 함수
from app.services.directions_utils import azimuth_to_direction  # 동서남북 변환 함수 import
from app.services.moon_phase_service import get_moon_phase_for_date, get_phase_description
from app.db.db_utils import retry_query, get_session  # get_session 함수 import
from app.services.sunrise_sunset_service import get_single_day_sunrise_sunset
from app import cache


@cache.memoize(timeout=30 * 24 * 60 * 60)  # 한 달 동안 캐시
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
        with get_session() as session:
            query = session.query(MeteorShowerInfo).filter(
                MeteorShowerInfo.name == shower_name,
                MeteorShowerInfo.peak_start_date.between(f"{year}-01-01", f"{year}-12-31")
            )

            # 쿼리 실행에 리트라이 기능 추가
            results = retry_query(session, query)

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


@cache.memoize(timeout=30 * 24 * 60 * 60)  # 한 달 동안 캐시
def find_best_peak_date(start_date, end_date, ra, dec, distance, latitude, longitude):
    preferred_phases = {
        "New Moon": 15,
        "Waxing Crescent": 10,
        "Waning Crescent": 10,
        "First Quarter": 5,
        "Last Quarter": 5,
        "Waxing Gibbous": -3,  # 보름달 직전
        "Waning Gibbous": -3,  # 보름달 직후
        "Full Moon": -5  # 보름달
    }

    # Peak Period 중앙값 계산
    mid_date = start_date + (end_date - start_date) / 2

    best_date = start_date
    best_time = None
    best_conditions = {
        "altitude": -1,
        "moon_phase": None,
        "illumination": None,
        "phase_description": None,
        "direction": None,
        "score": -1  # 점수를 추가로 평가
    }

    current_date = start_date
    while current_date <= end_date:
        for hour in range(0, 24):
            observation_time = current_date + timedelta(hours=hour)

            # 고도와 방위각 계산
            altitude, azimuth = calculate_altitude_azimuth(ra, dec, distance, latitude, longitude, 0, observation_time)

            # 방위각 -> 방향 변환
            direction = azimuth_to_direction(azimuth)

            # 달의 위상 정보 가져오기
            moon_phase_info = get_moon_phase_for_date(observation_time)
            if "error" in moon_phase_info:
                continue  # 오류가 있는 경우 건너뜀

            # `moon_phase_info`의 데이터를 그대로 사용
            moon_phase = moon_phase_info["moon_phase"]
            illumination = moon_phase_info["illumination"]
            phase_description = moon_phase_info["phase_description"]

            # 위상 가중치 계산
            phase_weight = preferred_phases.get(phase_description, 0)

            # 조명률에 따른 추가 점수 (0에 가까울수록 높은 점수)
            illumination_weight = max(0, (1 - illumination) * 10)  # 0 ~ 10 범위

            # 고도에 따른 추가 가중치
            altitude_weight = 0
            if altitude > 60:
                altitude_weight = 15  # 고도가 60° 이상이면 추가 점수
            elif altitude > 50:
                altitude_weight = 10  # 고도가 50~60° 사이면 보통 점수
            elif altitude > 30:
                altitude_weight = 5  # 고도가 30~50° 사이면 낮은 점수

            # 중앙값 날짜와의 거리 가중치
            days_from_mid = abs((current_date - mid_date).days)
            mid_date_weight = max(0, 10 - days_from_mid)  # 중앙 날짜에 가까울수록 높은 점수 (최대 10점)

            # 최종 점수 계산
            score = altitude + phase_weight + illumination_weight + altitude_weight + mid_date_weight

            # 조건 평가 (고도와 점수 기준)
            if score > best_conditions["score"]:
                best_date = current_date
                best_time = observation_time
                best_conditions = {
                    "altitude": altitude,
                    "moon_phase": moon_phase,
                    "illumination": illumination,
                    "phase_description": phase_description,
                    "direction": direction,
                    "score": score  # 점수 저장
                }
                print(f"Updated Best Conditions: {best_conditions}")

        current_date += timedelta(days=1)

    print(f"Best Date and Time: {best_time}, Final Conditions: {best_conditions}")
    return {"best_date": best_time, "conditions": best_conditions}


@cache.memoize(timeout=30 * 24 * 60 * 60)  # 한 달 동안 캐시
def evaluate_meteor_shower_visibility(shower_name, year, latitude, longitude):
    """
    특정 유성우의 가시성을 평가하는 함수
    """
    # 위도와 경도를 소수점 1자리로 반올림
    latitude = round(latitude, 1)
    longitude = round(longitude, 1)
    try:
        print(f"[INFO] Fetching meteor shower data for name: {shower_name}, year: {year}")
        meteor_shower_data = get_meteor_shower_data(shower_name, year)

        if isinstance(meteor_shower_data, dict) and "error" in meteor_shower_data:
            print(f"[ERROR] Meteor shower data fetch failed: {meteor_shower_data}")
            return meteor_shower_data

        if not meteor_shower_data:
            print(f"[WARNING] No meteor shower data found for name: {shower_name}, year: {year}")
            return {"error": "No meteor shower data found for the specified name and year."}

        visibility_results = []

        for data in meteor_shower_data:
            print(f"[INFO] Processing data for {data['name']} ({data['comet_name']})")
            # 피크 기간 중 가장 적합한 날짜 찾기
            best_peak = find_best_peak_date(
                datetime.fromisoformat(data["peak_start_date"]),
                datetime.fromisoformat(data["peak_end_date"]),
                data["ra"],
                data["declination"],
                data["distance"],
                latitude,
                longitude
            )

            best_date = best_peak["best_date"]
            best_conditions = best_peak["conditions"]
            print(f"[DEBUG] Best date: {best_date.date()}, Best conditions: {best_conditions}")

            # `best_date`가 datetime.date일 경우 변환
            if type(best_date) is datetime.date:
                best_date = datetime(best_date.year, best_date.month, best_date.day)

            print(f"[DEBUG] Calling get_single_day_sunrise_sunset with date: {best_date}")
            sunrise_sunset_info = get_single_day_sunrise_sunset(latitude, longitude, best_date)
            print(f"[DEBUG] Sunrise/Sunset info: {sunrise_sunset_info}")

            # 가시성 평가 메시지 계산
            visibility_score = best_conditions["score"]
            if visibility_score >= 80:
                visibility_rating = "Excellent"
            elif 60 <= visibility_score < 80:
                visibility_rating = "Good"
            elif 40 <= visibility_score < 60:
                visibility_rating = "Moderate"
            elif 20 <= visibility_score < 40:
                visibility_rating = "Poor"
            else:
                visibility_rating = "Very Poor"

            # 결과에 추가
            visibility_result = {
                "name": data["name"],
                "comet_name": data["comet_name"],
                "peak_period": data["peak_period"],
                "peak_dates": {
                    "start": data["peak_start_date"],
                    "end": data["peak_end_date"],
                    "best": best_date.isoformat()
                },
                "message": data["message"],
                "conditions": best_conditions,
                "coordinates": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "altitude": best_conditions["altitude"],
                    "moon_phase": best_conditions["moon_phase"],
                    "illumination": best_conditions["illumination"],
                    "direction": best_conditions["direction"]
                },
                "sun_times": {
                    "sunrise": sunrise_sunset_info.get("sunrise"),
                    "sunset": sunrise_sunset_info.get("sunset"),
                    "timeZoneId": sunrise_sunset_info.get("timeZoneId")
                },
                "visibility_message": f"Meteor shower is {visibility_rating.lower()}.",
                "visibility_rating": visibility_rating
            }

            # 가시성 판단
            if best_conditions["altitude"] <= 15.0:  # 고도 기준
                visibility_result["visibility_message"] = "Altitude is too low for visibility."
                visibility_result["visibility_rating"] = "Very Poor"

            visibility_results.append(visibility_result)

        print(f"[INFO] Final visibility results: {visibility_results}")
        return {"visibility_results": visibility_results}

    except Exception as e:
        print(f"[ERROR] Failed to evaluate meteor shower visibility: {e}")
        return {"error": f"Failed to evaluate meteor shower visibility: {e}"}
