# planet_routes.py

# planet_routes.py

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_restx import Api, Resource, Namespace

from app.services.planets.planet_opposition_service import predict_opposition_events
from app.services.planets.planet_visibility_service import calculate_planet_info
from app.services.planets.planet_event_storage_service import update_raw_data

# Namespace 생성
ns = Namespace('api/planets', description='Planet-related operations')


@ns.route('/visibility')
class PlanetVisibilityResource(Resource):
    @staticmethod
    @ns.doc(params={
        'planet': {
            'description': 'Name of the planet for visibility information (required)',
            'required': True,
            'example': 'Mars'
        },
        'lat': {
            'description': 'Latitude of the observation location (required)',
            'required': True,
            'example': 37.5665
        },
        'lon': {
            'description': 'Longitude of the observation location (required)',
            'required': True,
            'example': 126.9780
        },
        'date': {
            'description': 'The date for which you want to calculate the visibility in YYYY-MM-DD format (required)',
            'required': True,
            'example': '2024-10-01'
        },
        'range_days': {
            'description': 'Number of days to calculate visibility, default is 1 (optional)',
            'required': False,
            'example': 7
        }
    })
    @ns.response(200, 'Success')
    @ns.response(400, 'Invalid input format.')
    @ns.response(500, 'Internal server error.')
    def get():
        """
        행성 가시성 계산 API 엔드포인트

        쿼리 파라미터:
            - planet (str): 가시성 정보를 계산할 행성의 이름 (필수).
                            예시: Mars, Jupiter
            - lat (float): 관측 위치의 위도 (필수).
                           예시: 37.5665
            - lon (float): 관측 위치의 경도 (필수).
                           예시: 126.9780
            - date (str): 가시성 계산을 위한 날짜 (필수).
                          형식: YYYY-MM-DD
                          예시: 2024-10-01
            - range_days (int, 선택): 가시성을 계산할 기간 (일 수). 기본값은 1.

        반환값:
            JSON: 요청한 행성의 가시성 정보 또는 오류 메시지.
        """

        try:
            planet_name = request.args.get('planet')
            latitude = float(request.args.get('lat'))
            longitude = float(request.args.get('lon'))
            date_str = request.args.get('date')
            date = datetime.strptime(date_str, "%Y-%m-%d")
            range_days = int(request.args.get('range_days', 1))  # 기본값으로 1일 설정

            # 행성 가시성 정보 계산
            planet_info = calculate_planet_info(planet_name, latitude, longitude, date, range_days)
            return planet_info, 200

        except ValueError as ve:
            logging.error(f"Value error in planet visibility calculation: {str(ve)}")
            return {"error": "Invalid input format."}, 400
        except Exception as e:
            logging.error(f"Failed to calculate planet visibility: {str(e)}")
            return {"error": str(e)}, 500


@ns.route('/opposition')
class OppositionEventResource(Resource):
    @staticmethod
    @ns.doc(params={
        'planet': {
            'description': 'Name of the planet for opposition event prediction (required)',
            'required': True,
            'example': 'Jupiter'
        },
        'year': {
            'description': 'Year for predicting the opposition event (required)',
            'required': True,
            'example': 2024
        }
    })
    @ns.response(200, 'Success')
    @ns.response(400, 'Invalid input format.')
    @ns.response(500, 'Internal server error.')
    def get():
        """
        사용자가 요청한 행성의 대접근 예측을 반환하는 API 엔드포인트

        Query Parameters:
            - planet (str): Name of the planet for opposition event prediction.
                           Example: Jupiter
            - year (int): Year for predicting the opposition event.
                          Example: 2024

        Returns:
            JSON: Planet opposition event information or an error message.
        """
        try:
            planet_name = request.args.get('planet')
            year = request.args.get('year', type=int)

            # 필수 매개변수 검증
            if not planet_name or not year:
                return {"error": "Missing required parameters."}, 400

            # 대접근 이벤트 예측 호출
            result = predict_opposition_events(planet_name, year)

            return result, 200

        except ValueError as ve:
            logging.error(f"Value error in opposition prediction: {str(ve)}")
            return {"error": "Invalid input format."}, 400
        except Exception as e:
            logging.error(f"Failed to predict planet opposition: {str(e)}")
            return {"error": str(e)}, 500


@ns.route('/update_raw_data')
class UpdateRawDataResource(Resource):
    @staticmethod
    @ns.response(200, 'Opposition events data update started successfully.')
    @ns.response(500, 'Internal server error.')
    def post():
        """
        행성의 대접근 이벤트 데이터를 업데이트하는 API 엔드포인트
        """
        try:
            update_raw_data()
            return {"message": "Opposition events data update started successfully."}, 200
        except Exception as e:
            logging.error(f"Failed to update opposition events data: {str(e)}")
            return {"error": str(e)}, 500


# Blueprint와 API 설정
planet_blueprint = Blueprint('planets', __name__)
api = Api(planet_blueprint, version='1.0', title='Planet API', description='API Documentation for Planet Operations',
          doc='/api/docs')
api.add_namespace(ns)
