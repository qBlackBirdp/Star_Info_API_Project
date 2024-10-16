# get_timezone_info.py
from datetime import datetime

import requests
import os
import logging

# 로그 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_timezone_info(lat, lon, timestamp):
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
    logger.info(f"Requesting Google Time Zone API for lat: {lat}, lon: {lon}, timestamp: {timestamp}")

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")


def get_timezone_from_lat_lon(latitude, longitude, timestamp=None):
    print("============get_timezone_from_lat_lon 작동===============")
    """
    위도와 경도로부터 시간대 정보를 가져오는 함수 (Google Time Zone API 사용)

    Args:
        latitude (float): 위도
        longitude (float): 경도
        timestamp (int, optional): 타임스탬프 (초 단위). 기본적으로 현재 시간을 사용

    Returns:
        dict: 시간대 정보
    """
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
