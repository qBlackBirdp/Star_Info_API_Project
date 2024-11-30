# utils.py


from flask import request
from datetime import datetime, timedelta


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
