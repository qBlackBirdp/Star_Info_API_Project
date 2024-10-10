# global_resources.py
# skyfield 전역변수로 사용

# global_resources.py

from skyfield.api import load
import atexit

# 타임스케일 및 행성 데이터 로드 (전역 로드)
ts = load.timescale()
planets = load('de421.bsp')

# 애플리케이션 종료 시 planets 리소스 해제
atexit.register(planets.close)
