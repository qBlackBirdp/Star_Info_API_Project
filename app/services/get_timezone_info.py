# get_timezone_info.py

import requests
import os
import logging

# 로그 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_timezone_info(lat, lon, timestamp):
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
