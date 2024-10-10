# services/constellation_service.py

from skyfield.api import Topos, N, E, load_constellation_map, position_of_radec
from functools import lru_cache
from app.global_resources import ts, planets  # 전역 리소스 임포트

# 지구 객체 생성
earth = planets['earth']

# 별자리 데이터 로드
constellation_map = load_constellation_map()


@lru_cache(maxsize=128)
def get_constellation_for_date(latitude, longitude, year, month, day, hour, minute):
    """
    주어진 날짜와 위치(위도, 경도, 시간)에서의 별자리 정보를 반환하는 함수
    캐싱을 사용하여 최대 128개의 계산 결과를 저장해 성능 향상
    """
    t = ts.utc(year, month, day, hour, minute)  # 해당 날짜와 시간의 시간 객체 생성
    location = Topos(latitude * N, longitude * E)  # 위치 객체 생성
    observer = earth + location  # 관측자 위치 설정
    astrometric = observer.at(t)  # 관측 시점에서의 천체 위치 계산
    ra, dec, _ = astrometric.radec()  # 적경(ra)과 적위(dec) 계산

    # 적경과 적위를 이용해 별자리를 찾기
    position = position_of_radec(ra.hours, dec.degrees)
    constellation_name = constellation_map(position)

    return constellation_name  # 별자리 이름 반환


__all__ = ['get_constellation_for_date']
