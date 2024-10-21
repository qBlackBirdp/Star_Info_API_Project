# services/comet_approach_service.py
import traceback
from datetime import datetime
from app.services.horizons_service import get_comet_approach_events
from app.services.coordinate_converter import calculate_altitude


def get_comet_approach_data(comet_name, start_date, range_days=10, latitude=None, longitude=None):
    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        raw_data = get_comet_approach_events(comet_name, start_date_obj, range_days)

        if not raw_data or "error" in raw_data or not raw_data.get('data'):
            return {"error": "No comet approach data available."}

        analyzed_data = analyze_comet_data(raw_data['data'])

        if "error" in analyzed_data:
            return analyzed_data

        visibility_results = []

        if latitude is not None and longitude is not None:
            for approach_event in analyzed_data['sorted_data']:
                visibility_data = evaluate_comet_visibility(approach_event, latitude, longitude)
                # 가시성 있는 이벤트 및 가시성 이유를 함께 추가
                visibility_results.append({
                    "event_data": approach_event,
                    "visible_times": visibility_data.get("visible_times", []),
                    "reasons_for_no_visibility": visibility_data.get("reasons_for_no_visibility", []),
                    "message": visibility_data.get("message", "Visibility evaluation completed.")
                })

        # 가시성 있는 이벤트와 없는 이벤트를 나눔
        visible_events = [event for event in visibility_results if event['visible_times']]
        non_visible_events = [event for event in visibility_results if not event['visible_times']]

        # 가시성 있는 이벤트를 시간 순서대로 정렬
        sorted_visible_events = sorted(visible_events,
                                       key=lambda x: x['visible_times'][0]['local_time']) if visible_events else []

        # 가시성 있는 이벤트는 위에, 없는 이벤트는 아래에 배치
        sorted_visibility_results = sorted_visible_events + non_visible_events

        return {
            "closest_approach": {
                "data": analyzed_data['closest_approach'],
                "latitude": latitude,
                "longitude": longitude
            },
            "visibility_results": sorted_visibility_results
        }
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
        if not data:
            return {"error": "No data available for analysis."}

        # 접근 이벤트를 시간 순으로 정렬
        sorted_data = sorted(data, key=lambda x: datetime.strptime(x['time'], '%Y-%b-%d %H:%M'))

        if not sorted_data:
            return {"error": "Sorted data is empty."}

        # 지구와 가장 가까운 접근 이벤트 찾기
        closest_approach = min(sorted_data, key=lambda x: float(x['delta']))

        # 정렬된 접근 이벤트 리스트와 가장 가까운 접근 이벤트 반환
        return {
            "closest_approach": closest_approach,
            "sorted_data": sorted_data
        }
    except Exception as e:
        return {"error": f"Failed to analyze comet data: {str(e)}"}


def evaluate_comet_visibility(closest_approach_data, latitude, longitude):
    print("=============evaluate_comet_visibility===================")
    print(f"Evaluating visibility for comet approach: {closest_approach_data}")
    try:
        # 혜성의 접근 시간과 위치 정보
        approach_time_str = closest_approach_data['time']
        approach_time = datetime.strptime(approach_time_str, '%Y-%b-%d %H:%M')

        print(f"Approach Time: {approach_time}")

        # 혜성의 적경(RA), 적위(DEC), 거리(delta)를 Horizons API에서 받아옴
        ra_str = closest_approach_data['ra']  # 원본 RA 값
        dec_str = closest_approach_data['dec']  # 원본 Dec 값
        delta = float(closest_approach_data['delta'])  # 거리 (AU 단위)

        # 변환 확인 및 타입 출력
        print(f"Original RA: {ra_str}, Original Dec: {dec_str}")
        print(f"RA Type: {type(ra_str)}, Dec Type: {type(dec_str)}")

        # Skyfield를 사용해 고도(altitude) 계산
        elevation = 0
        alt = calculate_altitude(ra_str, dec_str, delta, latitude, longitude, elevation, approach_time)
        print(f"alt: {alt}")

        elongation = float(closest_approach_data.get('s-o-t', 0))  # 태양과의 각도 사용

        visible_times = []
        reasons_for_no_visibility = []

        # 가시성 판단 기준 추가: 고도와 태양과의 각도
        if alt <= 15.0:
            reasons_for_no_visibility.append(f"Altitude is too low ({alt}°). Must be greater than 15°.")
        if elongation <= 30.0:
            reasons_for_no_visibility.append(f"Solar elongation is too small ({elongation}°). Must be greater than 30°.")

        # 가시성 조건을 모두 만족하지 않을 경우 메시지 추가
        if reasons_for_no_visibility:
            return {
                "visible_times": [],  # 비어있는 visible_times 필드는 반환하지 않도록 수정
                "reasons_for_no_visibility": reasons_for_no_visibility,
                "message": "No visibility for the comet approach due to the following reasons."
            }

        # 조건을 모두 만족하는 경우에만 visible_times 필드를 추가
        visible_times.append({
            "data": closest_approach_data,
            "latitude": latitude,
            "longitude": longitude,
            "local_time": approach_time.strftime("%Y-%m-%d %H:%M (UTC 기준)"),
            "altitude": alt,
            "solar_elongation": elongation
        })

        return {
            "visible_times": visible_times,
            "reasons_for_no_visibility": reasons_for_no_visibility
        }
    except Exception as e:
        print("오류 발생:", str(e))  # 간단한 오류 메시지
        traceback.print_exc()  # 예외의 전체 스택 트레이스를 출력하여 디버깅에 도움을 줌
        return {"error": f"Failed to evaluate comet visibility: {str(e)}"}
