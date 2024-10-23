# services/comets/halley_service.py

from datetime import datetime, timedelta
from app.services.horizons_service import get_comet_approach_events
from app.services.comets.commet_utils import parse_ra_dec
from app.services.comets.comet_approach_service import analyze_comet_data


def get_halley_approach_data(start_date, range_days=365):
    try:
        # 시작 날짜 파싱
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')

        # 두 개의 6개월 구간에 대한 데이터를 각각 요청
        first_half_end_date = start_date_obj + timedelta(days=182)
        second_half_start_date = first_half_end_date + timedelta(days=1)

        # 첫 번째 6개월 구간
        first_half_data = get_comet_approach_events('Halley', start_date_obj, 182)
        if not first_half_data or "error" in first_half_data or not first_half_data.get('data'):
            return {"error": "No comet approach data available for the first half."}

        # 두 번째 6개월 구간
        second_half_data = get_comet_approach_events('Halley', second_half_start_date, 182)
        if not second_half_data or "error" in second_half_data or not second_half_data.get('data'):
            return {"error": "No comet approach data available for the second half."}

        # 데이터를 분석해서 각 구간에서 가장 가까운 접근 찾기
        closest_approach_first_half = analyze_comet_data(first_half_data['data'])
        if "error" in closest_approach_first_half:
            return closest_approach_first_half

        closest_approach_second_half = analyze_comet_data(second_half_data['data'])
        if "error" in closest_approach_second_half:
            return closest_approach_second_half

        # 두 접근 이벤트 반환
        return {
            "first_approach": closest_approach_first_half,
            "second_approach": closest_approach_second_half,
            "message": "Two closest approaches for Halley retrieved successfully."
        }

    except Exception as e:
        return {"error": f"Failed to get Halley approach data: {str(e)}"}
