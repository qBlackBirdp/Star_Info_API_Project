# global_resources.py
# skyfield 전역변수로 사용

from skyfield.api import position_of_radec, load, load_constellation_map
import atexit

# 타임스케일 및 행성 데이터 로드 (전역 로드)
ts = load.timescale()
planets = load('/de440.bsp')

# 지구 객체 생성 (전역 로드)
earth = planets['earth']

# 별자리 데이터 로드 (전역 로드)
constellation_map = load_constellation_map()

# 애플리케이션 종료 시 planets 리소스 해제
atexit.register(planets.close)
