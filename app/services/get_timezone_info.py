import json
from datetime import datetime
import requests
import os
from app import cache  # Flask-Caching import


@cache.memoize(timeout=43200)  # 캐싱 적용, 12시간 유효
def get_timezone_info(lat, lon, timestamp):
    """
    Google Time Zone API를 사용하여 시간대 정보를 가져오는 함수.

    Args:
        lat (float): 위도
        lon (float): 경도
        timestamp (int): 타임스탬프 (초 단위)

    Returns:
        dict: 시간대 정보
    """
    print("============get_timezone_info 작동===============")
    api_key = os.getenv('GOOGLE_TIMEZONE_API_KEY')
    if not api_key:
        raise ValueError("Google Time Zone API key is not set in environment variables.")

    base_url = "https://maps.googleapis.com/maps/api/timezone/json"
    params = {
        'location': f'{lat},{lon}',
        'timestamp': timestamp,
        'key': api_key
    }
    # 로그 추가 - API 요청 시 로그 남기기
    print(f"Requesting Google Time Zone API for lat: {lat}, lon: {lon}, timestamp: {timestamp}")
    print(f"Request parameters: {json.dumps(params)}")

    response = requests.get(base_url, params=params)

    # 로그 추가 - 응답 상태 코드와 내용 기록
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")


def get_timezone_from_lat_lon(latitude, longitude, timestamp=None):
    """
    위도와 경도로부터 시간대 정보를 가져오는 함수 (Google Time Zone API 사용)

    Args:
        latitude (float): 위도
        longitude (float): 경도
        timestamp (int, optional): 타임스탬프 (초 단위). 기본적으로 현재 시간을 사용

    Returns:
        dict: 시간대 정보
    """
    print("============get_timezone_from_lat_lon 작동===============")
    latitude = round(latitude, 2)
    longitude = round(longitude, 2)  # 캐싱 키 충돌 방지 위해 반올림

    if timestamp is None:
        timestamp = int(datetime.utcnow().timestamp())  # 현재 시간을 기준으로 타임스탬프 생성

    try:
        timezone_info = get_timezone_info(latitude, longitude, timestamp)
        return {
            'timeZoneId': timezone_info['timeZoneId'],
            'rawOffset': timezone_info['rawOffset'],
            'dstOffset': timezone_info.get('dstOffset', 0)
        }
    except Exception as e:
        print(f"Error fetching timezone information: {e}")
        return None
