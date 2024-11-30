# constellation_routes.py

# constellation_routes.py

import logging
from flask import Blueprint, request
from flask_restx import Api, Resource, Namespace

from app.utils import get_validated_params
from app.services.constellation.constellation_service import get_constellations_for_date_range
from app.services.constellation.constellation_visibility_service import calculate_visibility_for_constellations_parallel

# Namespace 생성 - Constellation 관련으로 명확하게 변경
ns = Namespace('api/constellations', description='Constellation-related operations')


@ns.route('/visibility')
class ConstellationsResource(Resource):
    @staticmethod
    @ns.doc(params={
        'lat': {
            'description': 'Latitude of the location for constellation visibility (required)',
            'required': True,
            'example': 37.5665
        },
        'lon': {
            'description': 'Longitude of the location for constellation visibility (required)',
            'required': True,
            'example': 126.9780
        },
        'start_date': {
            'description': 'Start date for constellation visibility in YYYY-MM-DD format (optional)',
            'required': True,
            'example': '2024-10-01'
        },
        'end_date': {
            'description': 'End date for constellation visibility in YYYY-MM-DD format (optional)',
            'required': False,
            'example': '2024-10-07'
        }
    })
    @ns.response(200, 'Success')
    @ns.response(400, 'Invalid input format or missing parameters.')
    @ns.response(500, 'Internal server error.')
    def get():
        """
        별자리 가시성 계산 API 엔드포인트 (제일 관측이 잘 되는 별자리 반환)

        사용자가 요청한 위도, 경도, 날짜 범위에 따라 별자리 정보를 반환합니다.

        Query Parameters:
            - lat (float): 위도. 별자리 가시성을 계산할 위치의 위도입니다.
                           예시: 37.5665
            - lon (float): 경도. 별자리 가시성을 계산할 위치의 경도입니다.
                           예시: 126.9780
            - start_date (str, 필수): 별자리 가시성 계산의 시작 날짜.
                                          형식: YYYY-MM-DD
                                          예시: 2024-10-01
            - end_date (str, 선택): 별자리 가시성 계산의 종료 날짜.
                                        형식: YYYY-MM-DD
                                        예시: 2024-10-07

        Returns:
            JSON: 별자리 가시성 정보 또는 오류 메시지를 반환합니다.
        """
        logging.debug("Received request for /api/constellations")
        print("=============별자리 로직 요청 받음==============")

        params, error_response, status_code = get_validated_params()
        if error_response:
            return error_response, status_code

        latitude, longitude, start_date, end_date = params[:4]

        try:
            constellation_data = get_constellations_for_date_range(latitude, longitude, start_date, end_date)
            constellation_data = calculate_visibility_for_constellations_parallel(constellation_data, latitude,
                                                                                  longitude)
            response_data = {
                "location": {"latitude": latitude, "longitude": longitude},
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d'),
                "constellations": constellation_data
            }
            return response_data, 200

        except Exception as e:
            logging.error(f"Error calculating constellations: {str(e)}")
            return {"error": f"Failed to calculate constellations: {str(e)}"}, 500


# Blueprint와 API 설정 - Constellation 관련으로 명확하게 변경
constellation_blueprint = Blueprint('constellations', __name__)
api = Api(constellation_blueprint, version='1.0', title='Constellation API',
          description='API Documentation for Constellation Operations', doc='/api/docs')
api.add_namespace(ns)
