# services/comet_approach_service.py

from app.services.horizons_service import get_comet_approach_events
from datetime import datetime


def get_comet_approach_data(comet_name, start_date, range_days=30):
    """
    주어진 혜성의 접근 이벤트 데이터를 반환하는 함수.

    Args:
        comet_name (str): 혜성 이름 (예: "Halley", "Encke").
        start_date (str): 검색 시작 날짜 (형식: 'YYYY-MM-DD').
        range_days (int, optional): 검색할 범위 일수. 기본값은 30일.

    Returns:
        dict: 혜성 접근 이벤트 데이터 또는 오류 메시지.
    """
    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        raw_data = get_comet_approach_events(comet_name, start_date_obj, range_days)

        if "error" in raw_data:
            return raw_data

        # 데이터 정리 및 분석
        return analyze_comet_data(raw_data['data'])
    except Exception as e:
        return {"error": f"Failed to get comet approach data: {str(e)}"}


def analyze_comet_data(data):
    """
    혜성 접근 이벤트 데이터를 정리하고 분석하는 함수.

    Args:
        data (list): 혜성 접근 이벤트 데이터 리스트.

    Returns:
        dict: 분석된 접근 이벤트 정보.
    """
    try:
        # 데이터 정리: 필요한 필드만 필터링하고 시간 순으로 정렬
        sorted_data = sorted(data, key=lambda x: datetime.strptime(x['time'], '%Y-%b-%d %H:%M'))

        # 가장 가까운 접근 시점 찾기
        closest_approach = min(sorted_data, key=lambda x: float(x['delta']))

        # 가시성 조건을 만족하는 시점 필터링
        visible_times = [entry for entry in sorted_data if float(entry['s-o-t']) > 40.0]

        return {
            "closest_approach": closest_approach,
            "visible_times": visible_times
        }
    except Exception as e:
        return {"error": f"Failed to analyze comet data: {str(e)}"}
