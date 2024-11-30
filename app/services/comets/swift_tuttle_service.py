# # services/comets/swift_tuttle_service.py

from datetime import datetime, timedelta
from app.services.horizons_service import get_comet_approach_events
from app.services.comets import analyze_comet_data
from app.services.comets import parse_ra_dec
from app.services.comets import detect_closing_or_receding


def get_swift_tuttle_approach_data(start_date, range_days=365):
    try:
        # 시작 날짜 파싱
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        print(f"[DEBUG] Start date object for Swift-Tuttle: {start_date_obj} (Type: {type(start_date_obj)})")

        # range_days가 None인 경우 기본값 설정
        if range_days is None:
            range_days = 365

        # 혜성 접근 이벤트 데이터 가져오기
        raw_data = get_comet_approach_events('Swift-Tuttle', start_date_obj, range_days)

        if not raw_data or "error" in raw_data or not raw_data.get('data'):
            return {"error": "No comet approach data available."}

        # 접근 이벤트 데이터 분석
        analyzed_data = analyze_comet_data(raw_data['data'])
        if "error" in analyzed_data:
            return analyzed_data

        sorted_data = analyzed_data['sorted_data']
        closest_approach = analyzed_data['closest_approach']

        # 혜성이 지구에서 멀어지고 있는지 판단
        detection_result = detect_closing_or_receding(sorted_data)
        print(f"[DEBUG] Detection result: {detection_result}")
        if "error" in detection_result:
            return detection_result

        if detection_result["status"] == "receding":
            # 멀어지고 있는 경우, 이후 가까워지는 접근 이벤트가 있다면 그 데이터를 사용
            next_closest_approach = detection_result.get("next_closest_approach")
            if next_closest_approach:
                closest_approach = next_closest_approach
            else:
                # closest_approach['time']을 datetime 객체로 변환
                approach_time = datetime.strptime(closest_approach['time'], '%Y-%b-%d %H:%M')
                # 멀어지고 있는 경우 다음 8월의 접근 데이터로 이동
                next_august = datetime(approach_time.year, 8, 10)
                if approach_time.month >= 8:
                    next_august = datetime(approach_time.year + 1, 8, 10)
                print(
                    f"[DEBUG] Next August date set to (after adjustment if needed): {next_august} (Type: {type(next_august)})")

                # 다음 8월로 접근 데이터를 가져오기
                raw_data = get_comet_approach_events('Swift-Tuttle', next_august, range_days)

                if not raw_data or "error" in raw_data or not raw_data.get('data'):
                    return {"error": "No comet approach data available for the adjusted date."}

                # 다시 접근 이벤트 데이터 분석
                analyzed_data = analyze_comet_data(raw_data['data'])
                if "error" in analyzed_data:
                    return analyzed_data

                closest_approach = analyzed_data['closest_approach']

        elif detection_result["status"] == "closing":
            # 가까워지고 있는 경우, 극대기 날짜로 이동하여 데이터 재요청
            peak_period_start = datetime.strptime(closest_approach['time'], '%Y-%b-%d %H:%M').replace(month=8, day=10)
            peak_period_end = peak_period_start + timedelta(days=14)
            closest_approach_time = datetime.strptime(closest_approach['time'], '%Y-%b-%d %H:%M')

            if not (peak_period_start <= closest_approach_time <= peak_period_end):
                print(
                    f"[DEBUG] Closest approach is not within peak period, adjusting date to peak period start: {peak_period_start}")
                raw_data = get_comet_approach_events('Swift-Tuttle', peak_period_start, range_days)

                if not raw_data or "error" in raw_data or not raw_data.get('data'):
                    return {"error": "No comet approach data available for the peak period date."}

                # 다시 접근 이벤트 데이터 분석
                analyzed_data = analyze_comet_data(raw_data['data'])
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
            "status": detection_result["status"],
            "closest_approach": closest_approach,
            "message": detection_result["message"]
        }

    except Exception as e:
        print(f"[ERROR] Error in get_swift_tuttle_approach_data: {str(e)}")
        return {"error": f"Failed to get Swift-Tuttle approach data: {str(e)}"}
