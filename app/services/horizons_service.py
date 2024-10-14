# services/horizons_service.py

import requests
from datetime import datetime, timedelta
from urllib.parse import quote

PLANET_CODES = {
    "Mercury": "199",
    "Venus": "299",
    "Earth": "399",
    "Moon": "301",
    "Mars": "499",
    "Phobos": "401",
    "Deimos": "402",
    "Jupiter": "599",
    "Io": "501",
    "Europa": "502",
    "Ganymede": "503",
    "Callisto": "504",
    "Saturn": "699",
    "Mimas": "601",
    "Enceladus": "602",
    "Tethys": "603",
    "Dione": "604",
    "Rhea": "605",
    "Titan": "606",
    "Uranus": "799",
    "Miranda": "701",
    "Ariel": "702",
    "Umbriel": "703",
    "Titania": "704",
    "Oberon": "705",
    "Neptune": "899",
    "Triton": "801",
    "Nereid": "802",
    "Pluto": "999",
    "Ceres": "1;",
    "Pallas": "2;",
    "Vesta": "3;",
    "Halley": "1P"
}


def get_planet_position_from_horizons(planet_name, date):
    planet_code = PLANET_CODES.get(planet_name)
    if not planet_code:
        return {"error": "Invalid planet name."}

    # 포맷 후 로그
    print(f"Formatted Date after: {date}")

    if isinstance(date, float):
        date = datetime.fromtimestamp(date)  # float를 datetime으로 변환

    # 포맷 후 로그
    print(f"Formatted Date Before: {date}")

    url = "https://ssd.jpl.nasa.gov/api/horizons.api"
    params = {
        "format": "json",
        "COMMAND": f"'{planet_code}'",
        "CENTER": "'500@399'",  # 지오센터 기준
        "MAKE_EPHEM": "YES",
        "EPHEM_TYPE": "OBSERVER",
        "OBJ_DATA": "YES",
        "START_TIME": f"'{date.strftime('%Y-%m-%d')}'",
        "STOP_TIME": f"'{(date + timedelta(days=1)).strftime('%Y-%m-%d')}'",
        "STEP_SIZE": "'1 h'",
        "QUANTITIES": "'1,9,20,23'"  # 필요한 데이터만 요청 (시간, 적경/적위, 태양 거리 등)
    }

    response = requests.get(url, params=params)
    print(f"Request URL: {response.url}")  # 요청 URL 로그
    print(f"Response Status Code: {response.status_code}")  # 응답 상태 코드 로그

    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Response Data: {data}")  # 응답 데이터 로그
            if 'result' in data:
                return data['result']
            else:
                return {"error": "Unexpected response format from Horizons API."}
        except ValueError:
            return {"error": "Failed to parse JSON response from Horizons API."}
    else:
        return {"error": f"Failed to retrieve data from Horizons API. Status code: {response.status_code}"}
