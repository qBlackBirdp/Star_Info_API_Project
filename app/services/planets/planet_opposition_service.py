# services/planet/planet_opposition_service.py

import logging

from app.data.data import get_opposition_au_threshold
from app.models.planet_raw_data import get_planet_raw_data_model
from app.db.db_utils import retry_query, get_session
from app import cache

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


@cache.memoize(timeout=3600)
def predict_opposition_events(planet_name, year, strict=False):
    """
    특정 행성의 대접근 이벤트를 예측하는 함수
    """
    events_list = []

    # 연도의 시작과 끝 날짜 설정 (화성과 금성의 경우 2년치 데이터를 조회)
    if planet_name in ["Mars", "Venus"]:
        years_to_query = [year, year + 1]
    else:
        years_to_query = [year]

    # `get_session` 사용
    with get_session() as session:
        try:
            threshold_strict = get_opposition_au_threshold(planet_name, strict=True)

            # 각 연도별로 테이블에서 데이터를 조회
            for query_year in years_to_query:
                PlanetRawDataYear = get_planet_raw_data_model(query_year)

                # 연도별 테이블에서 데이터 조회
                query = session.query(PlanetRawDataYear).filter(
                    PlanetRawDataYear.planet_name == planet_name,
                    PlanetRawDataYear.distance <= get_opposition_au_threshold(planet_name, strict)
                ).order_by(PlanetRawDataYear.distance.asc()).limit(5)

                rows = retry_query(session, query)

                for closest_event in rows:
                    reg_date = closest_event.reg_date
                    distance = closest_event.distance
                    s_o_t = closest_event.s_o_t
                    event_type = "planet big approach" if distance <= threshold_strict else "planet approach"
                    events_list.append({
                        "planet": planet_name,
                        "closest_date": reg_date.strftime("%Y-%m-%d"),
                        "distance_to_earth": f"{distance:.4f} AU",
                        "sun_observer_target_angle": f"{s_o_t:.2f}°",
                        "event_type": event_type
                    })

            if not events_list:
                return {"error": "No opposition events found for the requested year."}

        except Exception as e:
            logging.error(f"Database operation failed: {e}")
            session.rollback()  # 트랜잭션 복구
            return {"error": f"Database operation failed: {e}"}

    return events_list


__all__ = ['predict_opposition_events']
