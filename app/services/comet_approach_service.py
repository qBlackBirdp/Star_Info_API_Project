# services/comet_approach_service.py

from app.services.horizons_service import get_comet_approach_events
from datetime import datetime


def get_comet_approach_data(comet_name, start_date, range_days=30, latitude=None, longitude=None):
    """
    혜성 접근 이벤트 데이터를 반환하는 함수.

    Args:
        comet_name (str): 혜성 이름 (예: "Halley", "Encke").
        start_date (str): 검색 시작 날짜 (형식: 'YYYY-MM-DD').
        range_days (int, optional): 검색할 범위 일수. 기본값은 30일.
        latitude (float, optional): 사용자의 위도.
        longitude (float, optional): 사용자의 경도.

    Returns:
        dict: 혜성 접근 이벤트 데이터 또는 오류 메시지.
    """
    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        raw_data = get_comet_approach_events(comet_name, start_date_obj, range_days)

        if "error" in raw_data:
            return raw_data

        # 데이터 정리 및 분석
        analyzed_data = analyze_comet_data(raw_data['data'])

        # 사용자의 위치를 기반으로 가시성 판단
        if latitude is not None and longitude is not None:
            visibility_data = evaluate_comet_visibility(analyzed_data['closest_approach'], latitude, longitude)
        else:
            visibility_data = []

        # 최종 결과 반환
        return {
            "closest_approach": analyzed_data['closest_approach'],
            "visible_times": visibility_data
        }
    except Exception as e:
        return {"error": f"Failed to get comet approach data: {str(e)}"}


def analyze_comet_data(data):
    try:
        sorted_data = sorted(data, key=lambda x: datetime.strptime(x['time'], '%Y-%b-%d %H:%M'))
        closest_approach = min(sorted_data, key=lambda x: float(x['delta']))

        return {
            "closest_approach": closest_approach,
            "sorted_data": sorted_data
        }
    except Exception as e:
        return {"error": f"Failed to analyze comet data: {str(e)}"}


def evaluate_comet_visibility(closest_approach_data, latitude, longitude):
    """
    사용자의 위치를 기반으로 혜성 접근 이벤트의 가시성을 평가하는 함수.

    Args:
        closest_approach_data (dict): 가장 가까운 접근 이벤트 정보.
        latitude (float): 사용자의 위도.
        longitude (float): 사용자의 경도.

    Returns:
        list: 가시성이 좋은 시점 리스트.
    """
    try:
        # 가시성 판단 로직: 위도, 경도를 활용해 가시성 판단
        # 이 부분에서 추가적인 천문 계산을 통해 가시성을 평가할 수 있음.
        # 예를 들어, 지평선 위에 있는지 판단하거나 일정 고도 이상인지 확인
        visible_times = []

        # 예시: 단순히 s-o-t 값 기준으로 판단
        if float(closest_approach_data['s-o-t']) > 40.0:
            # 여기서 사용자의 위치를 고려한 더 정확한 가시성 로직을 구현
            # (추후에 태양과의 각도나 고도 등을 계산해서 추가)
            visible_times.append(closest_approach_data)

        return visible_times
    except Exception as e:
        return {"error": f"Failed to evaluate comet visibility: {str(e)}"}