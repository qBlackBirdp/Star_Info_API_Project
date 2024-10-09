# 모든 API 엔드포인트 정의

# app/routes.py

from flask import Blueprint, jsonify, request
from skyfield.api import load, Topos, N, E, load_constellation_map, position_of_radec
from skyfield.positionlib import ICRF
from datetime import datetime, timedelta
from functools import lru_cache

# Blueprint 객체 생성: 이 블루프린트를 사용해 라우트를 정의함
main = Blueprint('main', __name__)

# Skyfield에서 사용할 타임스케일 및 행성 데이터 로드
ts = load.timescale()
planets = load('de421.bsp')  # 행성 데이터 로드 (de421.bsp 파일 필요)
earth = planets['earth']  # 지구 객체 생성

# 별자리 데이터 로드
constellation_map = load_constellation_map()

# 간단한 캐시 구현 예시
@lru_cache(maxsize=128)
def get_constellation_for_date(latitude, longitude, year, month, day):
    """
    주어진 날짜와 위치(위도, 경도)에서의 별자리 정보를 반환하는 함수
    캐싱을 사용하여 최대 128개의 계산 결과를 저장해 성능 향상
    """
    t = ts.utc(year, month, day)  # 해당 날짜의 시간 객체 생성
    location = Topos(latitude * N, longitude * E)  # 위치 객체 생성
    observer = earth + location  # 관측자 위치 설정
    astrometric = observer.at(t)  # 관측 시점에서의 천체 위치 계산
    ra, dec, _ = astrometric.radec()  # 적경(ra)과 적위(dec) 계산

    # 적경과 적위를 이용해 별자리를 찾기
    position = position_of_radec(ra.hours, dec.degrees)
    constellation_name = constellation_map(position)
    return constellation_name  # 별자리 이름 반환

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
            constellation = get_constellation_for_date(latitude, longitude, current_date.year, current_date.month, current_date.day)
            # 결과를 리스트에 추가
            constellation_data.append({
                "date": current_date.strftime('%Y-%m-%d'),
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