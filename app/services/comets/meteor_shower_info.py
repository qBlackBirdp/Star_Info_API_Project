# services/comets/meteor_shower_info.py

from datetime import datetime
from app.data.data import METEOR_SHOWERS, LENIENT_CONDITIONS, COMET_PERIHELION_PEAK_OFFSET
from app.services.comets.comet_approach_service import get_comet_approach_data

ERROR_MARGIN_DAYS = 31  # 극대기의 추정 오차 범위 (±5일)


def get_meteor_shower_info(comet_name, start_date, range_days=365):
    """
    혜성과 관련된 유성우 정보를 반환하는 함수.

    Args:
        comet_name (str): 혜성의 이름.
        start_date (str): 혜성 접근 이벤트의 시작 날짜 (형식: '%Y-%m-%d').
        range_days (int): 검색할 기간 (기본값: 365일).

    Returns:
        list: 유성우 정보 리스트.
    """
    if comet_name.lower() == "halley":
        return get_meteor_shower_info_halley(comet_name, start_date, range_days)

    # 혜성 접근 이벤트 데이터 가져오기
    approach_data = get_comet_approach_data(comet_name, start_date, range_days)
    if "error" in approach_data:
        return approach_data

    closest_approach = approach_data.get('closest_approach')
    if not closest_approach:
        return {"error": "No closest approach data available."}

    approach_date = datetime.strptime(closest_approach['time'], '%Y-%b-%d %H:%M').date()
    meteor_showers = METEOR_SHOWERS.get(comet_name, [])

    shower_info_list = []

    for shower in meteor_showers:
        if shower.get("annual"):
            # 매년 규칙적으로 발생하는 유성우 평가
            start_month_day, end_month_day = shower['peak_period']
            start_month, start_day = map(int, start_month_day.split('-'))
            end_month, end_day = map(int, end_month_day.split('-'))

            # 유성우 극대기 기간 계산 (오차 범위 적용)
            peak_start_date = datetime(approach_date.year, start_month, start_day).date()
            peak_end_date = datetime(approach_date.year, end_month, end_day).date()

            # 접근 날짜와 극대기 간의 관계 파악
            if abs((approach_date - peak_start_date).days) <= ERROR_MARGIN_DAYS or abs(
                    (approach_date - peak_end_date).days) <= ERROR_MARGIN_DAYS:
                message = "Meteor shower peak period is near the comet approach date, increasing observation potential."
                conditions_used = "Lenient conditions applied"
            elif peak_start_date <= approach_date <= peak_end_date:
                message = "Meteor shower is at its peak period."
                conditions_used = "Standard conditions applied"
            else:
                message = "Meteor shower is not at its peak period."
                conditions_used = "Standard conditions applied"
        else:
            # 규칙적이지 않은 유성우 평가
            message = "Meteor shower occurrence is based on comet's closest approach and may vary."
            conditions_used = "Estimated conditions based on closest approach"

        # 극대기 시작일과 종료일 추가
        shower_info = {
            "name": shower["name"],
            "peak_period": shower.get("peak_period", "Based on comet's closest approach"),
            "peak_start_date": (
                datetime(approach_date.year, *map(int, shower["peak_period"][0].split('-'))).date().isoformat()
                if shower.get("annual") and "peak_period" in shower else "N/A"
            ),
            "peak_end_date": (
                datetime(approach_date.year, *map(int, shower["peak_period"][1].split('-'))).date().isoformat()
                if shower.get("annual") and "peak_period" in shower else "N/A"
            ),
            "message": message,
            "conditions_used": conditions_used,
            "status": approach_data.get("status", "unknown"),
            "comet_name": comet_name,
            "distance": closest_approach.get("delta", "unknown"),
            "ra": closest_approach.get("ra", "unknown"),
            "declination": closest_approach.get("dec", "unknown"),
        }

        shower_info_list.append(shower_info)

    return shower_info_list if shower_info_list else {
        "error": "No meteor shower information could be derived for the given period."}


def get_meteor_shower_info_halley(comet_name, start_date, range_days=365):
    """
    할리 혜성과 관련된 유성우 정보를 반환하는 함수.

    Args:
        comet_name (str): 혜성의 이름.
        start_date (str): 혜성 접근 이벤트의 시작 날짜 (형식: '%Y-%m-%d').
        range_days (int): 검색할 기간 (기본값: 365일).

    Returns:
        list: 유성우 정보 리스트.
    """
    approach_data = get_comet_approach_data(comet_name, start_date, range_days)
    if "error" in approach_data:
        return approach_data

    first_approach = approach_data.get('first_approach')
    second_approach = approach_data.get('second_approach')
    if not first_approach or not second_approach:
        return {"error": "No sufficient approach data available."}

    meteor_showers = METEOR_SHOWERS.get(comet_name, [])

    shower_info_list = []

    for shower in meteor_showers:
        if shower.get("annual"):
            # 첫 번째 접근 이벤트를 기준으로 유성우 평가
            approach_date = datetime.strptime(first_approach['time'], '%Y-%b-%d %H:%M').date()
            start_month_day, end_month_day = shower['peak_period']
            start_month, start_day = map(int, start_month_day.split('-'))
            end_month, end_day = map(int, end_month_day.split('-'))

            # 유성우 극대기 기간 계산 (오차 범위 적용)
            peak_start_date = datetime(approach_date.year, start_month, start_day).date()
            peak_end_date = datetime(approach_date.year, end_month, end_day).date()

            # 접근 날짜와 극대기 간의 관계 파악
            if abs((approach_date - peak_start_date).days) <= ERROR_MARGIN_DAYS or abs(
                    (approach_date - peak_end_date).days) <= ERROR_MARGIN_DAYS:
                message = "Meteor shower peak period is near the comet approach date, increasing observation potential."
                conditions_used = "Lenient conditions applied"
            elif peak_start_date <= approach_date <= peak_end_date:
                message = "Meteor shower is at its peak period."
                conditions_used = "Standard conditions applied"
            else:
                message = "Meteor shower is not at its peak period."
                conditions_used = "Standard conditions applied"

            # 극대기 시작일과 종료일 추가
            shower_info = {
                "name": shower["name"],
                "peak_period": shower.get("peak_period", "Based on comet's closest approach"),
                "peak_start_date": peak_start_date.isoformat(),
                "peak_end_date": peak_end_date.isoformat(),
                "message": message,
                "conditions_used": conditions_used,
                "status": first_approach.get("status", "unknown"),
                "comet_name": comet_name,
                "distance": first_approach.get("delta", "unknown"),
                "ra": first_approach.get("ra", "unknown"),
                "declination": first_approach.get("dec", "unknown"),
            }

            shower_info_list.append(shower_info)

    return shower_info_list if shower_info_list else None
