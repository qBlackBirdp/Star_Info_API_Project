# services/comet_approach_service.py

import traceback
from datetime import datetime, timedelta
from app.services.horizons_service import get_comet_approach_events
from app.data.data import COMET_CONDITIONS
from app.services.comets.commet_utils import parse_ra_dec, analyze_comet_data
from app.services.comets.halley_service import get_halley_approach_data


def get_comet_approach_data(comet_name, start_date, range_days=365):
    try:
        # 혜성별로 특화된 로직 처리
        comet_name_lower = comet_name.lower()
        if comet_name_lower == 'halley':
            return get_halley_approach_data(start_date, range_days)
        elif comet_name_lower == 'tuttle':
            return get_tuttle_approach_data(start_date, range_days)

        # 일반적인 혜성 접근 이벤트 요청 처리
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        raw_data = get_comet_approach_events(comet_name, start_date_obj, range_days)

        # 요청 결과 검증
        if not raw_data or "error" in raw_data or not raw_data.get('data'):
            return {"error": "No comet approach data available."}

        # 접근 이벤트 데이터 분석
        analyzed_data = analyze_comet_data(raw_data['data'])
        if "error" in analyzed_data:
            return analyzed_data

        # 접근 이벤트 데이터를 변환된 형태로 업데이트
        closest_approach = analyzed_data['closest_approach']
        ra_str = closest_approach['ra']
        dec_str = closest_approach['dec']
        converted_ra, converted_dec = parse_ra_dec(ra_str, dec_str)

        closest_approach['converted_ra'] = converted_ra
        closest_approach['converted_dec'] = converted_dec

        return {
            "closest_approach": closest_approach,
            "message": "Comet approach data retrieved successfully."
        }

    except Exception as e:
        return {"error": f"Failed to get comet approach data: {str(e)}"}
