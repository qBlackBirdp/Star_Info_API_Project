# services/comet_approach_service.py

from app.services.horizons_service import get_comet_approach_events
from datetime import datetime


def get_comet_approach_data(comet_name, start_date, range_days=30):
    """
    주어진 혜성의 접근 이벤트 데이터를 반환하는 함수.

    Args:
        comet_name (str): 혜성 이름 (예: "Halley", "Encke", "Biela").
        start_date (str): 검색 시작 날짜 (형식: 'YYYY-MM-DD').
        range_days (int, optional): 검색할 범위 일수. 기본값은 30일.

    Returns:
        dict: 혜성 접근 이벤트 데이터 또는 오류 메시지.
    """
    try:
        # 날짜 문자열을 datetime 객체로 변환
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')

        # Horizons API를 호출하여 혜성 접근 이벤트 데이터를 가져옴
        return get_comet_approach_events(comet_name, start_date_obj, range_days)
    except Exception as e:
        return {"error": f"Failed to get comet approach data: {str(e)}"}
