# services/comets/tuttle_service.py

from datetime import datetime, timedelta
from app.services.horizons_service import get_comet_approach_events
from app.services.comets import analyze_comet_data
from app.services.comets import parse_ra_dec


def get_tuttle_approach_data(start_date, range_days=365):
    try:
        # 시작 날짜 파싱
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        print(f"[DEBUG] Start date object for Tuttle: {start_date_obj} (Type: {type(start_date_obj)})")

        # 혜성 접근 이벤트 데이터 가져오기
        raw_data = get_comet_approach_events('Tuttle', start_date_obj, range_days)

        if not raw_data or "error" in raw_data or not raw_data.get('data'):
            return {"error": "No comet approach data available."}

        # 접근 이벤트 데이터 분석
        analyzed_data = analyze_comet_data(raw_data['data'])
        print(f"[DEBUG] Analyzed data for Tuttle: {analyzed_data}")
        if "error" in analyzed_data:
            return analyzed_data

        closest_approach = analyzed_data['closest_approach']

        # 혜성이 지구에서 멀어지고 있는지 판단
        deldot = float(closest_approach['deldot'])
        print(f"[DEBUG] Deldot value: {deldot}")
        approach_time_str = closest_approach['time']
        print(f"[DEBUG] Approach time string: {approach_time_str}")
        approach_time = datetime.strptime(approach_time_str, '%Y-%b-%d %H:%M')
        print(f"[DEBUG] Closest approach time object: {approach_time}")

        # 혜성이 멀어지고 있는 경우 다음 12월의 접근 데이터로 이동
        if deldot > 0:
            next_december = datetime(approach_time.year, 12, 1)
            print(f"[DEBUG] Next December date set to (before adjustment): {next_december} (Type: {type(next_december)})")
            if approach_time.month >= 12:
                next_december = datetime(approach_time.year + 1, 12, 1)
            print(f"[DEBUG] Next December date set to (after adjustment if needed): {next_december} (Type: {type(next_december)})")

            # 다음 12월로 접근 데이터를 가져오기
            raw_data = get_comet_approach_events('Tuttle', next_december, range_days)

            if not raw_data or "error" in raw_data or not raw_data.get('data'):
                return {"error": "No comet approach data available for the adjusted date."}

            # 다시 접근 이벤트 데이터 분석
            analyzed_data = analyze_comet_data(raw_data['data'])
            print(f"[DEBUG] Analyzed data for Tuttle after adjusting to December: {analyzed_data}")
            if "error" in analyzed_data:
                return analyzed_data

            closest_approach = analyzed_data['closest_approach']

        # 좌표 변환 처리
        ra_str = closest_approach['ra']
        dec_str = closest_approach['dec']
        print(f"[DEBUG] RA string: {ra_str}, DEC string: {dec_str}")
        converted_ra, converted_dec = parse_ra_dec(ra_str, dec_str)
        print(f"[DEBUG] Converted RA: {converted_ra}, Converted DEC: {converted_dec}")

        closest_approach['converted_ra'] = converted_ra
        closest_approach['converted_dec'] = converted_dec

        return {
            "closest_approach": closest_approach,
            "message": "Comet approach data retrieved successfully for Tuttle."
        }

    except Exception as e:
        print(f"[ERROR] Error in get_tuttle_approach_data: {str(e)}")
        return {"error": f"Failed to get Tuttle approach data: {str(e)}"}
