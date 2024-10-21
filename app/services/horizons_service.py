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
    "Halley": "1P",  # 할리 혜성 (주기: 약 76년, 오리온자리 유성우의 원인)
    "Encke": "2P",  # 엔케 혜성 (주기: 약 3.3년)
    "Faye": "4P",  # 파예 혜성 (주기: 약 7.5년)
    # "Brorsen": "5D",  # 브로르센 혜성 (소멸된 것으로 여겨짐)
    # "d'Arrest": "6P",  # 다레스트 혜성 (주기: 약 6.6년)
    # "Pons-Winnecke": "7P",  # 폰스-윈네케 혜성 (주기: 약 6.3년)
    "Tuttle": "8P",  # 터틀 혜성 (주기: 약 13.5년)
    # "Tempel 1": "9P",  # 템플 1 혜성 (주기: 약 5.5년)
    # "Tempel-Swift-LINEAR": "11P",  # 템플-스위프트-LINEAR 혜성 (주기: 약 6.4년)
    # "Olbers": "13P",  # 올버스 혜성 (주기: 약 69.5년)
    # "Wolf": "14P",  # 울프 혜성 (주기: 약 8.8년)
    # "Borrelly": "19P",  # 보렐리 혜성 (주기: 약 6.8년)
    "Giacobini-Zinner": "21P",  # 자코비니-진너 혜성 (주기: 약 6.6년, 드라코니드 유성우의 원인)
    # "Kopff": "22P",  # 콥프 혜성 (주기: 약 6.4년)
    "Grigg-Skjellerup": "26P",  # 그리그-셰를럽 혜성 (주기: 약 5.1년)
    # "Crommelin": "27P",  # 크롬멜린 혜성 (주기: 약 27.4년)
    # "Neujmin 1": "28P",  # 누이민 1 혜성 (주기: 약 18.2년)
    "Honda-Mrkos-Pajdusakova": "45P",  # 혼다-므르코스-파이두사코바 혜성 (주기: 약 5.3년)
    "Tempel-Tuttle": "55P",  # 템플-터틀 혜성 (주기: 약 33.2년, 레오니드 유성우의 원인)
    "Churyumov-Gerasimenko": "67P",  # 추류모프-게라시멘코 혜성 (주기: 약 6.5년, 로제타 탐사선으로 유명)
    # "Schwassmann-Wachmann 3": "73P",  # 슈바스만-바흐만 3 혜성 (주기: 약 5.4년)
    # "Kohoutek": "75P",  # 코후테크 혜성 (주기: 약 6.4년)
    "Wild 2": "81P",  # 와일드 2 혜성 (주기: 약 6.4년)
    # "Russell 2": "89P",  # 러셀 2 혜성 (주기: 약 7.6년)
    "Hartley-2": "103P",  # 하틀리 2 혜성 (주기: 약 6.5년)
    "Swift-Tuttle": "109P"  # 스위프트-터틀 혜성 (주기: 약 133년, 페르세우스 유성우의 원인)
    # "IRAS": "126P",  # IRAS 혜성 (주기: 약 13.6년)
    # "Machholz 2": "141P",  # 마흐홀츠 2 혜성 (주기: 약 5.2년)
    # "Ikeya-Zhang": "153P"  # 이케야-장 혜성 (주기: 약 366.5년)
}


def get_comet_record_number(comet_name):
    comet_code = COMET_CODES.get(comet_name)
    if not comet_code:
        return {"error": "Invalid comet name."}

    url = "https://ssd.jpl.nasa.gov/api/horizons.api"
    params = {
        "format": "text",  # 텍스트 형식으로 요청
        "COMMAND": f"'{comet_code}'",
        "OBJ_DATA": "NO"
    }

    response = requests.get(url, params=params)
    print(f"Request record-Num URL: {response.url}")
    print(f"Response Status Code: {response.status_code}")

    if response.status_code == 200:
        try:
            data = response.text  # 텍스트로 결과를 받음
            result_lines = data.splitlines()
            latest_record = None
            latest_year = float('-inf')

            # 각 줄을 출력하여 확인
            for line in result_lines:
                # print(f"Line: {line}")  # 각 줄을 로그로 출력

                # 레코드 번호가 있는 줄을 식별
                parts = line.split()
                if len(parts) >= 2 and parts[0].isdigit():
                    record_number = parts[0]
                    try:
                        epoch_year = int(parts[1])  # 연도 추출
                        # 최신 연도를 가진 레코드 선택
                        if epoch_year > latest_year:
                            latest_year = epoch_year
                            latest_record = record_number
                    except ValueError:
                        continue

            if latest_record:
                print(f"Extracted Latest Record Number: {latest_record}")
                return latest_record
            else:
                return {"error": "Failed to extract the latest record number."}
        except Exception as e:
            print(f"Parsing error: {e}")
            return {"error": "Failed to parse response from Horizons API."}
    else:
        return {"error": f"Failed to retrieve data from Horizons API. Status code: {response.status_code}"}


def get_comet_approach_events(comet_name, date, range_days):
    record_number = get_comet_record_number(comet_name)
    if isinstance(record_number, dict) and "error" in record_number:
        return record_number

    if isinstance(date, float):
        date = datetime.fromtimestamp(date)

    if range_days == 1:
        end_date = date + timedelta(days=1)
    else:
        end_date = date + timedelta(days=range_days)

    url = "https://ssd.jpl.nasa.gov/api/horizons.api"
    params = {
        "format": "json",
        "COMMAND": f"'{record_number}'",
        "CENTER": "'500@399'",  # 지오센터 기준
        "MAKE_EPHEM": "YES",
        "EPHEM_TYPE": "OBSERVER",
        "OBJ_DATA": "YES",
        "START_TIME": f"'{date.strftime('%Y-%m-%d')}'",
        "STOP_TIME": f"'{end_date.strftime('%Y-%m-%d')}'",
        "STEP_SIZE": "'1 d'",
        "QUANTITIES": "'1,2,19,20,23,25'"  # 필요한 데이터만 요청 (시간, 태양 거리, 궤도 요소, 적경/적위, 속도)
    }

    response = requests.get(url, params=params)
    print(f"Request Comet URL: {response.url}")
    print(f"Response Status Code: {response.status_code}")

    if response.status_code == 200:
        try:
            data = response.json()
            if 'result' in data:
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

                parsed_dict = []
                for entry in parsed_data:
                    parts = entry.split()
                    if len(parts) >= 11:  # Ensure there are enough parts to parse correctly
                        parsed_dict.append({
                            "comet_name": comet_name,
                            "time": f"{parts[0]} {parts[1]}",  # TIME
                            "ra": f"{parts[2]} {parts[3]} {parts[4]}",  # Right Ascension (RA)
                            "dec": f"{parts[5]} {parts[6]} {parts[7]}",  # Declination (DEC)
                            "delta": parts[14],  # Solar distance
                            "deldot": parts[15],  # Radial velocity
                            "s-o-t": parts[16]  # Sun-Observer-Target angle
                        })
                    else:
                        print(f"Skipping line due to unexpected format: {entry}")

                # print("Parsed Data:")
                # for item in parsed_dict:
                #      print(item)

                return {"data": parsed_dict}
            else:
                return {"error": "Unexpected response format from Horizons API."}
        except ValueError as e:
            print(f"JSON parsing error: {e}")
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
