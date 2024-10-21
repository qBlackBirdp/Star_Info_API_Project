# 모든 API 엔드포인트 정의
# app/routes.py

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta

from .services.comet_approach_service import get_comet_approach_data
from .services.get_timezone_info import get_timezone_info
from .services.constellation_service import get_constellations_for_date_range
from .services.planet_visibility_service import calculate_planet_info
from .services.sunrise_sunset_service import calculate_sunrise_sunset_for_range
from .services.planet_event_storage_service import update_raw_data
from .services.constellation_visibility_service import calculate_visibility_for_constellations_parallel
from .services.planet_opposition_service import predict_opposition_events

# Blueprint 객체 생성: 이 블루프린트를 사용해 라우트를 정의함
main = Blueprint('main', __name__)


def get_validated_params():
    """
    공통으로 사용하는 위도, 경도, 날짜 등의 파라미터를 검증 및 반환하는 함수
    단일 날짜와 날짜 범위 둘 다 처리할 수 있음.
    """
    # 쿼리 파라미터로부터 위도, 경도, 날짜 정보 받기
    latitude = request.args.get('lat')
    longitude = request.args.get('lon')
    date_str = request.args.get('date')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    hour = request.args.get('hour', default=0, type=int)
    minute = request.args.get('minute', default=0, type=int)

    # 위도와 경도 입력 여부 확인
    if not latitude or not longitude:
        return None, {"error": "Latitude and Longitude are required"}, 400

    # 위도와 경도 값을 실수(float)로 변환
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return None, {"error": "Invalid Latitude or Longitude format"}, 400

    # 단일 날짜 처리
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return None, {"error": "Invalid date format. Use YYYY-MM-DD."}, 400
        return (latitude, longitude, date, date, hour, minute), None, None

    # 날짜 범위 처리
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else datetime.now()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else start_date + timedelta(days=90)
    except ValueError:
        return None, {"error": "Invalid date format. Use YYYY-MM-DD."}, 400

    # 날짜 범위 검증
    if start_date > end_date or (end_date - start_date).days > 365:
        return None, {"error": "Invalid date range."}, 400

    return (latitude, longitude, start_date, end_date, hour, minute), None, None


@main.route('/api/constellations', methods=['GET'])
def get_constellations():
    """
    사용자가 요청한 위도, 경도, 날짜 범위에 따라 별자리 정보를 반환하는 API 엔드포인트
    """
    print("=============별자리 로직 요청 받음==============")
    params, error_response, status_code = get_validated_params()
    if error_response:
        return jsonify(error_response), status_code

    latitude, longitude, start_date, end_date = params[:4]  # hour와 minute 제거

    try:
        # 별자리 정보 계산 (날짜 범위에 대해 한 번만 호출)
        constellation_data = get_constellations_for_date_range(latitude, longitude, start_date, end_date)
        print(f"Constellation Data after range calculation: {constellation_data}")

        # 각 별자리에 대해 가시성이 가장 좋은 시간대 계산
        constellation_data = calculate_visibility_for_constellations_parallel(constellation_data, latitude, longitude)

    except Exception as e:
        print(f"Error calculating constellations: {str(e)}")
        return jsonify({"error": f"Failed to calculate constellations: {str(e)}"}), 500

    # 최종 결과를 JSON으로 반환
    return jsonify({
        "location": {"latitude": latitude, "longitude": longitude},
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "constellations": constellation_data
    })


@main.route('/api/sunrise_sunset', methods=['GET'])
def get_sunrise_sunset():
    """
    사용자가 요청한 위도, 경도, 날짜 범위에 따라 일출 및 일몰 시간을 반환하는 API 엔드포인트
    """
    params, error_response, status_code = get_validated_params()
    if error_response:
        return jsonify(error_response), status_code

    latitude, longitude, start_date, end_date, _, _ = params

    # 첫 번째 날짜에 대해 타임존 정보 가져오기
    try:
        timezone_info = get_timezone_info(latitude, longitude, int(start_date.timestamp()))
        offset_sec = timezone_info['rawOffset'] + timezone_info.get('dstOffset', 0)
    except Exception as e:
        return jsonify({"error": f"Failed to get time zone information: {str(e)}"}), 500

    # 일출 및 일몰 시간 계산 (여러 날짜에 대해 한 번에)
    sunrise_sunset_data = calculate_sunrise_sunset_for_range(latitude, longitude, start_date, end_date, offset_sec)

    # 최종 결과를 JSON으로 반환
    return jsonify({
        "location": {"latitude": latitude, "longitude": longitude},
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "sunrise_sunset": sunrise_sunset_data
    })


@main.route('/api/planet_visibility', methods=['GET'])
def get_planet_visibility():
    try:
        planet_name = request.args.get('planet')
        latitude = float(request.args.get('lat'))
        longitude = float(request.args.get('lon'))
        date_str = request.args.get('date')
        date = datetime.strptime(date_str, "%Y-%m-%d")
        range_days = int(request.args.get('range_days', 1))  # 기본값으로 1일 설정

        # 행성 가시성 정보 계산
        planet_info = calculate_planet_info(planet_name, latitude, longitude, date, range_days)
        return jsonify(planet_info)

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@main.route('/api/opposition', methods=['GET'])
def get_opposition_event():
    """
    사용자가 요청한 행성의 대접근 예측을 반환하는 API 엔드포인트
    """
    try:
        planet_name = request.args.get('planet')
        year = request.args.get('year', type=int)

        # 필수 매개변수 검증
        if not planet_name or not year:
            return jsonify({"error": "Missing required parameters."}), 400

        # 대접근 이벤트 예측 호출
        result = predict_opposition_events(planet_name, year)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route('/api/update_raw_data', methods=['POST'])
def update_opposition_events():
    try:
        update_raw_data()
        return jsonify({"message": "Opposition events data update started successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route('/api/comet_approach', methods=['GET'])
def get_comet_approach():
    """
    사용자가 요청한 혜성 접근 이벤트 정보를 반환하는 API 엔드포인트
    """
    try:
        comet_name = request.args.get('comet')
        start_date_str = request.args.get('start_date')
        range_days = request.args.get('range_days', type=int, default=30)

        # 추가: 위치 정보 받기
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)

        # 필수 매개변수 검증
        if not comet_name or not start_date_str:
            return jsonify({"error": "Missing required parameters: 'comet' and 'start_date' are required."}), 400

        # 날짜 문자열을 datetime 객체로 변환
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

        # 혜성 접근 이벤트 데이터 가져오기
        result = get_comet_approach_data(comet_name, start_date.strftime('%Y-%m-%d'), range_days, latitude, longitude)

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Failed to get comet approach: {str(e)}"}), 500

