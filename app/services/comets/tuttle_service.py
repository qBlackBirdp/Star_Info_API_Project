# services/comets/tuttle_service.py

from datetime import datetime, timedelta
from app.services.horizons_service import get_comet_approach_events
from app.services import analyze_comet_data


def get_tuttle_approach_data(start_date, range_days=365):
    try:
        # 시작 날짜 파싱
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')

        # 혜성 접근 이벤트 데이터 가져오기
        raw_data = get_comet_approach_events('Tuttle', start_date_obj, range_days)

        if not raw_data or "error" in raw_data or not raw_data.get('data'):
            return {"error": "No comet approach data available."}

        # 접근 이벤트 데이터 분석
        analyzed_data = analyze_comet_data(raw_data['data'])
        if "error" in analyzed_data:
            return analyzed_data

        closest_approach = analyzed_data['closest_approach']

        # 혜성이 지구에서 멀어지고 있는지 판단
        deldot = float(closest_approach['deldot'])
        approach_time = datetime.strptime(closest_approach['time'], '%Y-%b-%d %H:%M')

        # 혜성이 멀어지고 있는 경우 다음 12월의 접근 데이터로 이동
        if deldot > 0:
            next_december = datetime(approach_time.year, 12, 1)
            if approach_time.month > 12:
                next_december = datetime(approach_time.year + 1, 12, 1)

            # 12월로 다시 접근 데이터를 가져옴
            raw_data = get_comet_approach_events('Tuttle', next_december.strftime('%Y-%m-%d'), range_days)

            if not raw_data or "error" in raw_data or not raw_data.get('data'):
                return {"error": "No comet approach data available for the adjusted date."}

            # 다시 접근 이벤트 데이터 분석
            analyzed_data = analyze_comet_data(raw_data['data'])
            if "error" in analyzed_data:
                return analyzed_data

            closest_approach = analyzed_data['closest_approach']

        return {
            "closest_approach": closest_approach,
            "message": "Comet approach data retrieved successfully for Tuttle."
        }

    except Exception as e:
        return {"error": f"Failed to get Tuttle approach data: {str(e)}"}