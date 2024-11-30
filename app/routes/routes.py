# 모든 API 엔드포인트 정의
# app/routes.py

from flask import Blueprint
from flask_restx import Api

# 각 엔드포인트별 Blueprint를 import
from app.routes.comet_routes import comet_blueprint, ns as comet_ns
from app.routes.constellations_routes import constellation_blueprint, ns as constellation_ns
from app.routes.meteor_shower_routes import meteor_shower_blueprint, ns as meteor_ns
from app.routes.moon_phase_routes import moon_phase_blueprint, ns as moon_ns
from app.routes.planet_routes import planet_blueprint, ns as planet_ns
from app.routes.sunrise_sunset_routes import sunrise_sunset_blueprint, ns as sunrise_ns

# 메인 Blueprint 생성
main = Blueprint('main', __name__)

# Flask-RestX API 객체 생성 (Swagger UI 설정)
api = Api(main, version='1.0', title='Astronomical Events API', description='API Documentation for Astronomical Events',
          doc='/api/docs')

# Blueprint와 API 등록
# 각 엔드포인트별 Blueprint 등록
main.register_blueprint(comet_blueprint, url_prefix='/api/comets')
print(f"Blueprint {comet_blueprint.name} registered with URL prefix '/api/comets'")

main.register_blueprint(constellation_blueprint, url_prefix='/api/constellations')
print(f"Blueprint {constellation_blueprint.name} registered with URL prefix '/api/constellations'")

main.register_blueprint(meteor_shower_blueprint, url_prefix='/api/meteor_showers')
print(f"Blueprint {meteor_shower_blueprint.name} registered with URL prefix '/api/meteor_showers'")

main.register_blueprint(moon_phase_blueprint, url_prefix='/api/moon_phase')
print(f"Blueprint {moon_phase_blueprint.name} registered with URL prefix '/api/moon_phase'")

main.register_blueprint(planet_blueprint, url_prefix='/api/planets')
print(f"Blueprint {planet_blueprint.name} registered with URL prefix '/api/planets'")

main.register_blueprint(sunrise_sunset_blueprint, url_prefix='/api/sunrise_sunset')
print(f"Blueprint {sunrise_sunset_blueprint.name} registered with URL prefix '/api/sunrise_sunset'")

# 각 네임스페이스를 최종적으로 API 객체에 추가
api.add_namespace(comet_ns)
api.add_namespace(constellation_ns)
api.add_namespace(meteor_ns)
api.add_namespace(moon_ns)
api.add_namespace(planet_ns)
api.add_namespace(sunrise_ns)

__all__ = ["main"]
