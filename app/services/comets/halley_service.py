# services/comets/halley_service.py

from datetime import datetime, timedelta
from app.services.horizons_service import get_comet_approach_events
from app.services.comets.commet_utils import parse_ra_dec, detect_closing_or_receding
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
        analyzed_data_first_half = analyze_comet_data(first_half_data['data'])
        if "error" in analyzed_data_first_half:
            return analyzed_data_first_half

        analyzed_data_second_half = analyze_comet_data(second_half_data['data'])
        if "error" in analyzed_data_second_half:
            return analyzed_data_second_half

        sorted_data_first_half = analyzed_data_first_half['sorted_data']
        closest_approach_first_half = analyzed_data_first_half['closest_approach']

        sorted_data_second_half = analyzed_data_second_half['sorted_data']
        closest_approach_second_half = analyzed_data_second_half['closest_approach']

        # 첫 번째 구간에서 혜성이 지구에서 멀어지고 있는지 판단
        detection_result_first_half = detect_closing_or_receding(sorted_data_first_half)
        if "error" in detection_result_first_half:
            return detection_result_first_half

        if detection_result_first_half["status"] == "receding":
            # 멀어지고 있는 경우, 이후 다시 가까워지는 접근 이벤트가 있다면 그 데이터를 사용
            next_closest_approach = detection_result_first_half.get("next_closest_approach")
            if next_closest_approach:
                closest_approach_first_half = next_closest_approach
            else:
                # 멀어지는 경우, 다음 5월의 접근 데이터로 이동
                next_may = datetime.strptime(closest_approach_first_half['time'], '%Y-%b-%d %H:%M').replace(month=5,
                                                                                                            day=1)
                first_half_data = get_comet_approach_events('Halley', next_may, 182)
                if not first_half_data or "error" in first_half_data or not first_half_data.get('data'):
                    return {"error": "No comet approach data available for the adjusted date."}
                analyzed_data_first_half = analyze_comet_data(first_half_data['data'])
                if "error" in analyzed_data_first_half:
                    return analyzed_data_first_half
                closest_approach_first_half = analyzed_data_first_half['closest_approach']
        elif detection_result_first_half["status"] == "closing":
            # 가까워지는 경우 극대기에 맞춰서 데이터를 조정
            peak_period_start = datetime.strptime(closest_approach_first_half['time'], '%Y-%b-%d %H:%M').replace(
                month=5, day=1)
            peak_period_end = peak_period_start + timedelta(days=14)
            closest_approach_time = datetime.strptime(closest_approach_first_half['time'], '%Y-%b-%d %H:%M')
            if not (peak_period_start <= closest_approach_time <= peak_period_end):
                closest_approach_first_half['time'] = peak_period_start.strftime('%Y-%b-%d %H:%M')
        else:
            # 계속 멀어지는 경우
            closest_approach_first_half['status'] = 'receding'

        # 두 번째 구간에서 혜성이 지구에서 멀어지고 있는지 판단
        detection_result_second_half = detect_closing_or_receding(sorted_data_second_half)
        if "error" in detection_result_second_half:
            return detection_result_second_half

        if detection_result_second_half["status"] == "receding":
            # 멀어지고 있는 경우, 이후 다시 가까워지는 접근 이벤트가 있다면 그 데이터를 사용
            next_closest_approach = detection_result_second_half.get("next_closest_approach")
            if next_closest_approach:
                closest_approach_second_half = next_closest_approach
            else:
                # 멀어지는 경우, 다음 10월의 접근 데이터로 이동
                next_october = datetime.strptime(closest_approach_second_half['time'], '%Y-%b-%d %H:%M').replace(
                    month=10, day=8)
                second_half_data = get_comet_approach_events('Halley', next_october, 182)
                if not second_half_data or "error" in second_half_data or not second_half_data.get('data'):
                    return {"error": "No comet approach data available for the adjusted date."}
                analyzed_data_second_half = analyze_comet_data(second_half_data['data'])
                if "error" in analyzed_data_second_half:
                    return analyzed_data_second_half
                closest_approach_second_half = analyzed_data_second_half['closest_approach']
        elif detection_result_second_half["status"] == "closing":
            # 가까워지는 경우 극대기에 맞춰서 데이터를 조정
            peak_period_start = datetime.strptime(closest_approach_second_half['time'], '%Y-%b-%d %H:%M').replace(
                month=10, day=8)
            peak_period_end = peak_period_start + timedelta(days=37)
            closest_approach_time = datetime.strptime(closest_approach_second_half['time'], '%Y-%b-%d %H:%M')
            if not (peak_period_start <= closest_approach_time <= peak_period_end):
                closest_approach_second_half['time'] = peak_period_start.strftime('%Y-%b-%d %H:%M')
        else:
            # 계속 멀어지는 경우
            closest_approach_second_half['status'] = 'receding'

        # 좌표 변환 처리 (첫 번째 구간)
        ra_str_first = closest_approach_first_half['ra']
        dec_str_first = closest_approach_first_half['dec']
        converted_ra_first, converted_dec_first = parse_ra_dec(ra_str_first, dec_str_first)
        closest_approach_first_half['converted_ra'] = converted_ra_first
        closest_approach_first_half['converted_dec'] = converted_dec_first
        closest_approach_first_half['status'] = detection_result_first_half['status']

        # 좌표 변환 처리 (두 번째 구간)
        ra_str_second = closest_approach_second_half['ra']
        dec_str_second = closest_approach_second_half['dec']
        converted_ra_second, converted_dec_second = parse_ra_dec(ra_str_second, dec_str_second)
        closest_approach_second_half['converted_ra'] = converted_ra_second
        closest_approach_second_half['converted_dec'] = converted_dec_second
        closest_approach_second_half['status'] = detection_result_second_half['status']

        # 두 접근 이벤트 반환
        return {
            "first_approach": closest_approach_first_half,
            "second_approach": closest_approach_second_half,
            "message": "Two closest approaches for Halley retrieved successfully."
        }

    except Exception as e:
        return {"error": f"Failed to get Halley approach data: {str(e)}"}
