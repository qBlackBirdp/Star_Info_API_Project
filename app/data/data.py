# data.py

# 과거 관측 데이터를 기반으로 한 혜성별 유성우 극대기까지의 평균 일 수
COMET_PERIHELION_PEAK_OFFSET = {
    "Halley": 75,  # 에타 아쿠아리드 유성우는 근일점 통과 후 약 75일 뒤 극대기 발생
    # "Encke": 50,  # 타우리드 유성우는 근일점 통과 후 약 50일 뒤 극대기 발생
    "Tuttle": 80,  # 우르시드 유성우는 근일점 통과 후 약 80일 뒤 극대기 발생
    "Giacobini-Zinner": 40,  # 드라코니드 유성우는 근일점 통과 후 약 40일 뒤 극대기 발생
    "Tempel-Tuttle": 100,  # 레오니드 유성우는 근일점 통과 후 약 100일 뒤 극대기 발생
    "Schwassmann-Wachmann": 60,  # 타우 헤르쿨리드 유성우는 근일점 통과 후 약 60일 뒤 극대기 발생
    "Swift-Tuttle": 70  # 페르세이드 유성우는 근일점 통과 후 약 70일 뒤 극대기 발생
}

COMET_CONDITIONS = {
    "Giacobini-Zinner": {
        "min_altitude": 10.0,  # 최소 고도 (10도)
        "min_elongation": 20.0  # 최소 신축각 (20도)
    },
    "Halley": {
        "min_altitude": 15.0,  # 최소 고도 (15도)
        "min_elongation": 30.0  # 최소 신축각 (30도)
    },
    "Tempel-Tuttle": {
        "min_altitude": 12.0,  # 최소 고도 (12도)
        "min_elongation": 25.0  # 최소 신축각 (25도)
    },
    # "Encke": {
    #     "min_altitude": 8.0,  # 최소 고도 (8도)
    #     "min_elongation": 15.0  # 최소 신축각 (15도)
    # },
    "Swift-Tuttle": {
        "min_altitude": 18.0,  # 최소 고도 (18도)
        "min_elongation": 35.0  # 최소 신축각 (35도)
    },
    "Schwassmann-Wachmann": {
        "min_altitude": 10.0,  # 최소 고도 (10도)
        "min_elongation": 20.0  # 최소 신축각 (20도)
    },
    "Tuttle": {
        "min_altitude": 14.0,  # 최소 고도 (14도)
        "min_elongation": 25.0  # 최소 신축각 (25도)
    },
    # 필요에 따라 추가적인 혜성 조건들을 계속 추가 가능
}

LENIENT_CONDITIONS = {
    "min_altitude": 5.0,  # 최소 고도 (5도)
    "min_elongation": 10.0  # 최소 신축각 (10도)
}

METEOR_SHOWERS = {
    "Halley": [
        {
            "name": "Eta Aquariid",
            "peak_period": ["05-02", "05-06"],  # 극대기 날짜를 4일로 확장
            "annual": True
        },
        {
            "name": "Orionid",
            "peak_period": ["10-19", "10-23"],  # 극대기 중심으로 4일로 확장
            "annual": True
        }
    ],
    "Tuttle": [
        {
            "name": "Ursid",
            "peak_period": ["12-21", "12-24"],  # 피크 기간을 4일로 확장
            "annual": True
        }
    ],
    "Swift-Tuttle": [
        {
            "name": "Perseid",
            "peak_period": ["08-11", "08-14"],  # 극대기 4일로 확장
            "annual": True
        }
    ]
}

# 비주기 메테오
NON_ANNUAL_METEOR_SHOWERS = {
    # "Encke": [
    #     {
    #         "name": "Taurid",
    #         "estimated_peak_period": "Based on comet's closest approach",  # 혜성 접근 주기에 따라 발생
    #         "annual": False
    #     }
    # ],
    "Giacobini-Zinner": [
        {
            "name": "Draconid",
            "estimated_peak_period": "Based on comet's closest approach",  # 혜성 접근 주기에 따라 발생
            "annual": False
        }
    ],
    "Tempel-Tuttle": [
        {
            "name": "Leonid",
            "estimated_peak_period": "Based on comet's closest approach",  # 혜성 접근 주기에 따라 발생
            "annual": False
        }
    ],
    "Schwassmann-Wachmann": [
        {
            "name": "Tau Herculid",
            "estimated_peak_period": "Based on comet's closest approach",  # 혜성 접근 주기에 따라 발생
            "annual": False
        }
    ]
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
    # "Encke": "2P",  # 엔케 혜성 (주기: 약 3.3년)
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
