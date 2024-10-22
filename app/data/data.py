# data.py

METEOR_SHOWERS = {
    "Halley": [
        {"name": "Eta Aquariid", "peak_period": ("04-20", "05-10")},
        {"name": "Orionid", "peak_period": ("10-02", "11-07")}
    ],
    "Encke": [{"name": "Taurid", "peak_period": ("10-20", "11-30")}],
    "Tuttle": [{"name": "Ursid", "peak_period": ("12-17", "12-26")}],
    "Giacobini-Zinner": [{"name": "Draconid", "peak_period": ("10-06", "10-10")}],
    "Tempel-Tuttle": [{"name": "Leonid", "peak_period": ("11-15", "11-20")}],
    "Schwassmann-Wachmann": [{"name": "Tau Herculid", "peak_period": ("05-25", "06-10")}],
    "Swift-Tuttle": [{"name": "Perseid", "peak_period": ("08-10", "08-15")}]
}

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
    "Halley": "1P",  # 할리 혜성 (주기: 약 76년, 오리온자리 유성우 및 에타 아쿠아리드 유성우의 원인)
    "Encke": "2P",  # 엔케 혜성 (주기: 약 3.3년)
    "Tuttle": "8P",  # 터틀 혜성 (주기: 약 13.5년, 우르시드 유성우의 원인)
    "Giacobini-Zinner": "21P",  # 자코비니-진너 혜성 (주기: 약 6.6년, 드라코니드 유성우의 원인)
    "Tempel-Tuttle": "55P",  # 템플-터틀 혜성 (주기: 약 33.2년, 레오니드 유성우의 원인)
    "Schwassmann-Wachmann": "73P",  # 슈바스만-바흐만 혜성 (주기: 약 5.4년, 타우 헤르쿨리드 유성우의 원인)
    "Swift-Tuttle": "109P"  # 스위프트-터틀 혜성 (주기: 약 133년, 페르세우스 유성우의 원인)
}


# Skyfield에서 사용하는 행성 이름과 코드 간의 매핑
def get_skyfield_planet_code(planet_name):
    planet_name_map = {
        "Mercury": "Mercury",
        "Venus": "Venus",
        "Earth": "Earth",
        "Mars": "Mars barycenter",
        "Jupiter": "Jupiter barycenter",
        "Saturn": "Saturn barycenter",
        "Uranus": "Uranus barycenter",
        "Neptune": "Neptune barycenter",
        "Pluto": "Pluto barycenter"
    }
    return planet_name_map.get(planet_name)


# DB에 사용할 행성 코드와 이름 간의 매핑
def get_db_planet_code(planet_name):
    planet_name_map = {
        "Mercury": 199,
        "Venus": 299,
        "Earth": 399,
        "Mars": 499,
        "Jupiter": 599,
        "Saturn": 699,
        "Uranus": 799,
        "Neptune": 899,
        "Pluto": 999
    }
    return planet_name_map.get(planet_name)


# 행성별 대접근 기준 AU 값을 정의하는 매핑 함수
def get_opposition_au_threshold(planet_name, strict=False):
    opposition_au_thresholds = {
        "Mercury": (0.56, 0.60),
        "Venus": (0.30, 0.50),
        "Mars": (0.643, 0.70),
        "Jupiter": (4.1, 4.4),
        "Saturn": (8.33, 8.66),
        "Uranus": (18.40, 18.60),
        "Neptune": (28.87, 28.90),
        "Pluto": (34.1, 34.8)
    }
    return opposition_au_thresholds.get(planet_name, (None, None))[0 if strict else 1]
