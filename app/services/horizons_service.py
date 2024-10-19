# services/horizons_service.py

import requests
from datetime import datetime, timedelta

PLANET_CODES = {
    "Mercury": "199",
    "Venus": "299",
    "Earth": "399",
    "Mars": "499",
    "Jupiter": "599",
    "Saturn": "699",
    "Uranus": "799",
    "Neptune": "899",
    "Pluto": "999",
    "Moon": "301",
    "Phobos": "401",
    "Deimos": "402",
    "Io": "501",
    "Europa": "502",
    "Ganymede": "503",
    "Callisto": "504",
    "Mimas": "601",
    "Enceladus": "602",
    "Tethys": "603",
    "Dione": "604",
    "Rhea": "605",
    "Titan": "606",
    "Miranda": "701",
    "Ariel": "702",
    "Umbriel": "703",
    "Titania": "704",
    "Oberon": "705",
    "Triton": "801",
    "Nereid": "802",
    "Ceres": "1;",
    "Pallas": "2;",
    "Vesta": "3;"
}

COMET_CODES = {
    "Halley": "1P",
    "Encke": "2P",
    "Biela": "3P"
}


def get_comet_approach_events(comet_name, date, range_days):
    comet_code = COMET_CODES.get(comet_name)
    if not comet_code:
        return {"error": "Invalid comet name."}

    # 포맷 전 로그
    # print(f"Formatted Date Before: {date}")

    if isinstance(date, float):
        date = datetime.fromtimestamp(date)  # float를 datetime으로 변환

    # 포맷 후 로그
    # print(f"Formatted Date After: {date}")

    # 단일 날짜 요청 처리
    if range_days == 1:
        end_date = date + timedelta(days=1)
    else:
        end_date = date + timedelta(days=range_days)

    url = "https://ssd.jpl.nasa.gov/api/horizons.api"
    params = {
        "format": "json",
        "COMMAND": f"'{comet_code}'",
        "CENTER": "'500@399'",  # 지오센터 기준
        "MAKE_EPHEM": "YES",
        "EPHEM_TYPE": "OBSERVER",
        "OBJ_DATA": "YES",
        "START_TIME": f"'{date.strftime('%Y-%m-%d')}'",
        "STOP_TIME": f"'{end_date.strftime('%Y-%m-%d')}'",
        "STEP_SIZE": "'1 d'",
        "QUANTITIES": "'1,2,20,23,24,25'"
    }

    response = requests.get(url, params=params)
    print(f"Request URL: {response.url}")  # 요청 URL 로그
    print(f"Response Status Code: {response.status_code}")  # 응답 상태 코드 로그

    if response.status_code == 200:
        try:
            data = response.json()
            # print(f"Response Data: {data}")  # 응답 데이터 로그
            if 'result' in data:
                # 파싱 로직 추가
                result_lines = data['result'].splitlines()
                parsed_data = []
                extracting = False
                for line in result_lines:
                    if "$SOE" in line:
                        extracting = True
                        continue
                    elif "$EOE" in line:
                        extracting = False
                        break
                    if extracting:
                        parsed_data.append(line)
                # print(f"Parsed Data: {parsed_data}")  # 파싱된 데이터 로그

                # 파싱된 데이터를 딕셔너리 형태로 변환
                parsed_dict = []
                for entry in parsed_data:
                    parts = entry.split()
                    parsed_dict.append({
                        "time": f"{parts[0]} {parts[1]}",
                        "ra": f"{parts[2]} {parts[3]} {parts[4]}",
                        "dec": f"{parts[5]} {parts[6]} {parts[7]}",
                        "delta": parts[8],
                        "s-o-t": parts[10]
                    })
                # print(f"Parsed Dictionary: {parsed_dict}")  # 딕셔너리 형태의 파싱 데이터 로그
                return {"data": parsed_dict}
            else:
                return {"error": "Unexpected response format from Horizons API."}
        except ValueError as e:
            print(f"JSON parsing error: {e}")  # JSON 파싱 에러 로그
            return {"error": "Failed to parse JSON response from Horizons API."}
    else:
        return {"error": f"Failed to retrieve data from Horizons API. Status code: {response.status_code}"}


def get_planet_position_from_horizons(planet_name, date, range_days):
    planet_code = PLANET_CODES.get(planet_name)
    if not planet_code:
        return {"error": "Invalid planet name."}
    # 요청 유형에 따른 처리
    if planet_name in PLANET_CODES:
        request_type = "planet"
    else:
        request_type = "comet"

    print(f"planet_code: {planet_code}")
    # 포맷 전 로그
    # print(f"Formatted Date Before: {date}")

    if isinstance(date, float):
        date = datetime.fromtimestamp(date)  # float를 datetime으로 변환

    # 포맷 후 로그
    # print(f"Formatted Date After: {date}")

    # 단일 날짜 요청 처리
    if range_days == 1:
        end_date = date + timedelta(days=1)
    else:
        end_date = date + timedelta(days=range_days)

    url = "https://ssd.jpl.nasa.gov/api/horizons.api"
    params = {
        "format": "json",
        "COMMAND": f"'{planet_code}'",
        "CENTER": "'500@399'",  # 지오센터 기준
        "MAKE_EPHEM": "YES",
        "EPHEM_TYPE": "OBSERVER",
        "OBJ_DATA": "YES",
        "START_TIME": f"'{date.strftime('%Y-%m-%d')}'",
        "STOP_TIME": f"'{end_date.strftime('%Y-%m-%d')}'",
        "STEP_SIZE": "'1 d'",
        "QUANTITIES": "'1,20,23'"  # 필요한 데이터만 요청 (시간, 적경/적위, 태양 거리)
    }

    # 포맷 후 로그
    # print(f"Formatted Parameters: {params}")

    response = requests.get(url, params=params)
    print(f"Request URL: {response.url}")  # 요청 URL 로그
    print(f"Response Status Code: {response.status_code}")  # 응답 상태 코드 로그

    if response.status_code == 200:
        try:
            data = response.json()
            # print(f"Response Data: {data}")  # 응답 데이터 로그
            if 'result' in data:
                # 파싱 로직 추가
                result_lines = data['result'].splitlines()
                parsed_data = []
                extracting = False
                for line in result_lines:
                    if "$SOE" in line:
                        extracting = True
                        continue
                    elif "$EOE" in line:
                        extracting = False
                        break
                    if extracting:
                        parsed_data.append(line)
                # print(f"Parsed Data: {parsed_data}")  # 파싱된 데이터 로그

                # 파싱된 데이터를 딕셔너리 형태로 변환
                parsed_dict = []
                for entry in parsed_data:
                    parts = entry.split()
                    parsed_dict.append({
                        "time": f"{parts[0]} {parts[1]}",
                        "ra": f"{parts[2]} {parts[3]} {parts[4]}",
                        "dec": f"{parts[5]} {parts[6]} {parts[7]}",
                        "delta": parts[8],
                        "s-o-t": parts[10]
                    })
                # print(f"Parsed Dictionary: {parsed_dict}")  # 딕셔너리 형태의 파싱 데이터 로그
                return {"data": parsed_dict}
            else:
                return {"error": "Unexpected response format from Horizons API."}
        except ValueError as e:
            print(f"JSON parsing error: {e}")  # JSON 파싱 에러 로그
            return {"error": "Failed to parse JSON response from Horizons API."}
    else:
        return {"error": f"Failed to retrieve data from Horizons API. Status code: {response.status_code}"}
