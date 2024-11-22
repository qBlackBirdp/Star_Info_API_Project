# services/planet/planet_visibility_service.py

from datetime import datetime, timedelta
from skyfield import almanac
from skyfield.api import Topos
from app.global_resources import ts, planets  # 전역 리소스 임포트
from app.services.sunrise_sunset_service import calculate_sunrise_sunset_for_range  # 일출 및 일몰 계산 함수 import
from app.services.timezone_conversion_service import convert_utc_to_local_time  # 시간 변환 함수 import
from app.data.data import get_skyfield_planet_code
from app.models.planet_raw_data import get_planet_raw_data_model
from app.services.directions_utils import azimuth_to_direction
from app.db.db_utils import retry_query, get_session  # get_session 추가
from app import cache


@cache.memoize(timeout=3600)
def calculate_planet_info(planet_name, latitude, longitude, date, range_days=1, timezone_info=None):
    """
    주어진 위치와 날짜에 대한 특정 행성의 가시성 및 위치 정보를 반환하는 함수
    """
    latitude = round(latitude, 4)
    longitude = round(longitude, 4)
    # 위치 설정
    location = Topos(latitude, longitude)

    # 타임존 정보가 제공되지 않은 경우, sunrise_sunset_data_list에서 가져옴
    if not timezone_info:
        sunrise_sunset_data_list = calculate_sunrise_sunset_for_range(
            latitude, longitude, date, date + timedelta(days=range_days - 1)
        )
        if not sunrise_sunset_data_list or "error" in sunrise_sunset_data_list[0]:
            return [{"error": "Failed to calculate sunrise or sunset."}]

        timezone_info = {
            'timeZoneId': sunrise_sunset_data_list[0].get('timeZoneId', 'Unknown'),
            'offset_sec': sunrise_sunset_data_list[0].get('offset', 0)
        }

    # 지정된 범위에 대한 일출 및 일몰 정보 가져오기
    end_date = date + timedelta(days=range_days - 1)
    sunrise_sunset_data_list = calculate_sunrise_sunset_for_range(latitude, longitude, date, end_date)

    if not sunrise_sunset_data_list or "error" in sunrise_sunset_data_list[0]:
        return [{"error": "Failed to calculate sunrise or sunset."}]

    # Skyfield에서 사용할 행성 이름으로 변환
    skyfield_planet_code = get_skyfield_planet_code(planet_name)
    if not skyfield_planet_code:
        return [{"error": f"Invalid planet name for Skyfield: {planet_name}"}]

    # 천체력에서 행성 가져오기
    planet = planets[skyfield_planet_code]

    # get_session을 사용하여 세션 관리
    with get_session() as session:
        try:
            # DB에서 데이터 조회
            PlanetRawDataYear = get_planet_raw_data_model(date.year)
            query = session.query(PlanetRawDataYear).filter(
                PlanetRawDataYear.planet_name == planet_name,
                PlanetRawDataYear.reg_date.between(date, end_date)
            )

            rows = retry_query(session, query)

            if not rows:
                return [{"error": f"No data available for {planet_name} in the specified date range."}]

            results = []

            for row, sunrise_sunset_data in zip(rows, sunrise_sunset_data_list):
                reg_date = row.reg_date
                delta = row.distance
                s_o_t = row.s_o_t

                t0 = ts.utc(reg_date.year, reg_date.month, reg_date.day, 0, 0, 0)
                t1 = ts.utc(reg_date.year, reg_date.month, reg_date.day, 23, 59, 59)
                times, is_visible = almanac.find_discrete(
                    t0, t1, almanac.risings_and_settings(planets, planet, location)
                )

                # 가시성 판단 추가 로직 (고도를 고려)
                visible = False
                best_time = None

                # 행성의 고도와 방위각 계산
                apparent = (planets['earth'] + location).at(t0).observe(planet).apparent()
                alt, az, _ = apparent.altaz()
                altitude = alt.degrees

                for t, visible_event in zip(times, is_visible):
                    if visible_event == 1:  # 행성이 떠오르는 시간
                        # 고도가 0 이상일 때만 visible로 설정
                        if altitude >= 0:
                            visible = True
                            best_time = convert_utc_to_local_time(
                                t.utc_datetime(), timezone_info['offset_sec']
                            ).time()
                        break

                # 고도와 일출/일몰 시간에 따라 visibility_judgment 설정
                sunrise_time = datetime.fromisoformat(sunrise_sunset_data['sunrise']).time()
                sunset_time = datetime.fromisoformat(sunrise_sunset_data['sunset']).time()

                if best_time:
                    if best_time > sunset_time or best_time < sunrise_time:
                        # 일몰 이후 또는 일출 이전이라면
                        if altitude >= 45:
                            visibility_judgment = (
                                "Good visibility - The planet is high in the sky and it's dark enough for easy observation."
                            )
                        else:
                            visibility_judgment = (
                                "Difficult to observe - The planet is visible, but it is low in the sky, making it harder to see."
                            )
                    else:
                        # 일출 이후 일몰 이전
                        if altitude >= 45:
                            visibility_judgment = (
                                "Difficult to observe - The planet is high, but daylight might make it challenging to see."
                            )
                        else:
                            visibility_judgment = (
                                "Not recommended - The planet is low in the sky and daylight makes it very hard to observe."
                            )
                else:
                    visibility_judgment = "No optimal observation time available."

                # 방위각을 동서남북 방향으로 변환
                azimuth = az.degrees
                direction = azimuth_to_direction(azimuth)

                results.append(
                    {
                        "date": reg_date.strftime("%Y-%m-%d"),
                        "visible": visible,
                        "best_time": best_time.strftime("%H:%M") if best_time else "N/A",
                        "timeZoneId": timezone_info['timeZoneId'],
                        "offset_sec": timezone_info['offset_sec'],
                        "distance_to_earth": f"{delta:.4f} AU" if delta else "N/A",
                        "altitude": f"{altitude:.2f}°",
                        "azimuth": direction,
                        "visibility_judgment": visibility_judgment,
                        "sunrise": sunrise_sunset_data['sunrise'],
                        "sunset": sunrise_sunset_data['sunset'],
                    }
                )

        except Exception as e:
            return [{"error": f"Database operation failed: {e}"}]

    return results
