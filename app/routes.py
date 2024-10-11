# 모든 API 엔드포인트 정의

# app/routes.py

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from .services.constellation_service import get_constellation_for_date
from .services.sunrise_sunset_service import calculate_sunrise_sunset
from app.services.planet_visibility_service import calculate_planet_info

# Blueprint 객체 생성: 이 블루프린트를 사용해 라우트를 정의함
main = Blueprint('main', __name__)


@main.route('/api/constellations', methods=['GET'])
def get_constellations():
    """
    사용자가 요청한 위도, 경도, 날짜 범위에 따라 별자리 정보를 반환하는 API 엔드포인트
    """
    # 쿼리 파라미터로부터 위도, 경도, 날짜 범위 정보 받기
    latitude = request.args.get('lat')
    longitude = request.args.get('lon')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    hour = request.args.get('hour', default=0, type=int)
    minute = request.args.get('minute', default=0, type=int)

    # 위도와 경도 입력 여부 확인
    if not latitude or not longitude:
        return jsonify({"error": "Latitude and Longitude are required"}), 400

    # 위도와 경도 값을 실수(float)로 변환
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return jsonify({"error": "Invalid Latitude or Longitude format"}), 400

    # 날짜 유효성 검사 및 변환
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else datetime.now()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else start_date + timedelta(days=90)
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    # 날짜 범위 검증
    if start_date > end_date or (end_date - start_date).days > 365:
        return jsonify({"error": "Invalid date range."}), 400

    # 결과를 저장할 리스트 초기화
    constellation_data = []
    current_date = start_date
    # 날짜 범위를 하루씩 증가시키면서 별자리 정보 계산
    while current_date <= end_date:
        try:
            # 캐시된 결과를 사용해 별자리 계산
            constellation = get_constellation_for_date(latitude, longitude, current_date.year, current_date.month,
                                                       current_date.day, hour, minute)
            # 결과를 리스트에 추가
            constellation_data.append({
                "date": current_date.strftime('%Y-%m-%d'),
                "time": f"{hour:02d}:{minute:02d}",
                "constellations": constellation
            })
        except Exception as e:
            # 별자리 계산 실패 시 에러 메시지 반환
            return jsonify({"error": f"Failed to calculate constellation: {str(e)}"}), 500

        # 날짜를 하루 증가
        current_date += timedelta(days=1)

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
    사용자가 요청한 위도, 경도, 날짜에 따라 일출 및 일몰 시간을 반환하는 API 엔드포인트
    """
    # 쿼리 파라미터로부터 위도, 경도, 날짜 정보 받기
    latitude = request.args.get('lat')
    longitude = request.args.get('lon')
    date_str = request.args.get('date')

    # 위도와 경도 입력 여부 확인
    if not latitude or not longitude or not date_str:
        return jsonify({"error": "Latitude, Longitude, and Date are required"}), 400

    # 위도와 경도 값을 실수(float)로 변환
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return jsonify({"error": "Invalid Latitude or Longitude format. Please provide valid numerical values."}), 400

    # 날짜 유효성 검사 및 변환
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    # 일출 및 일몰 시간 계산
    try:
        sunrise_sunset_data = calculate_sunrise_sunset(latitude, longitude, date)
    except ValueError as ve:
        return jsonify({"error": f"Value error during sunrise and sunset calculation: {str(ve)}"}), 500
    except RuntimeError as re:
        return jsonify({"error": f"Runtime error during sunrise and sunset calculation: {str(re)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Failed to calculate sunrise and sunset: {str(e)}"}), 500

    # 최종 결과를 JSON으로 반환
    return jsonify({
        "location": {"latitude": latitude, "longitude": longitude},
        "date": date.strftime('%Y-%m-%d'),
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

        # 행성 가시성 정보 계산
        planet_info = calculate_planet_info(planet_name, latitude, longitude, date)
        return jsonify(planet_info)

    except Exception as e:
        return jsonify({"error": str(e)}), 400

