# get_timezone_info.py

import requests
import os


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

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
