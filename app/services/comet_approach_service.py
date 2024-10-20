# services/comet_approach_service.py

from app.services.horizons_service import get_comet_approach_events
from datetime import datetime


def get_comet_approach_data(comet_name, start_date, range_days=30):
    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        raw_data = get_comet_approach_events(comet_name, start_date_obj, range_days)

        if "error" in raw_data:
            return raw_data

        # 데이터 정리 및 분석
        analyzed_data = analyze_comet_data(raw_data['data'])

        # 추가로 가시성 판단을 요청할 경우 별도 로직으로 처리
        visibility_data = evaluate_comet_visibility(analyzed_data['closest_approach'])

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


def evaluate_comet_visibility(closest_approach_data):
    """
    혜성 접근 이벤트 데이터를 바탕으로 가시성을 평가하는 함수.

    Args:
        closest_approach_data (dict): 가장 가까운 접근 이벤트 정보.

    Returns:
        list: 가시성이 좋은 시점 리스트.
    """
    try:
        # 가시성 판단 로직: 여기서 지구에서의 위치나 다른 변수들을 고려해 추가 로직 구현
        # 예시로 간단하게 s-o-t 값을 확인
        visible_times = []
        if float(closest_approach_data['s-o-t']) > 40.0:
            visible_times.append(closest_approach_data)

        return visible_times
    except Exception as e:
        return {"error": f"Failed to evaluate comet visibility: {str(e)}"}
