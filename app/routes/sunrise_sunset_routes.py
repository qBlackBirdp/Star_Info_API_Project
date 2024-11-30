# sunrise_sunset_routes.py

from flask import Blueprint, request
from flask_restx import Api, Resource, Namespace

from app.utils import get_validated_params
from app.services.get_timezone_info import get_timezone_info
from app.services.sunrise_sunset_service import calculate_sunrise_sunset_for_range

# Namespace 생성
ns = Namespace('api/sunrise_sunset', description='Sunrise and Sunset related operations')


@ns.route('/time')
class SunriseSunsetResource(Resource):
    @staticmethod
    @ns.doc(params={
        'lat': {
            'description': 'Latitude of the location (required)',
            'required': True,
            'example': 37.5665
        },
        'lon': {
            'description': 'Longitude of the location (required)',
            'required': True,
            'example': 126.9780
        },
        'start_date': {
            'description': 'Start date for the sunrise and sunset times in YYYY-MM-DD format (optional)',
            'required': True,
            'example': '2024-10-01'
        },
        'end_date': {
            'description': 'End date for the sunrise and sunset times in YYYY-MM-DD format (optional)',
            'required': False,
            'example': '2024-10-07'
        }
    })
    @ns.response(200, 'Success')
    @ns.response(400, 'Invalid input format or missing parameters.')
    @ns.response(500, 'Internal server error.')
    def get():
        """
        일출 및 일몰 시간 계산 API 엔드포인트

        사용자가 요청한 위도, 경도, 날짜 범위에 따라 일출 및 일몰 시간을 반환합니다.

        쿼리 매개변수:
            - lat (float): 관측 위치의 위도.
                           예시: 37.5665
            - lon (float): 관측 위치의 경도.
                           예시: 126.9780
            - start_date (str, 필수): 일출 및 일몰 시간을 계산할 시작 날짜.
                                          형식: YYYY-MM-DD
                                          예시: 2024-10-01
            - end_date (str, 선택): 일출 및 일몰 시간을 계산할 종료 날짜.
                                        형식: YYYY-MM-DD
                                        예시: 2024-10-07

        반환 값:
            JSON: 요청한 일출 및 일몰 시간 정보 또는 오류 메시지.
        """

        params, error_response, status_code = get_validated_params()
        if error_response:
            return error_response, status_code

        latitude, longitude, start_date, end_date, _, _ = params

        # 첫 번째 날짜에 대해 타임존 정보 가져오기
        try:
            timezone_info = get_timezone_info(latitude, longitude, int(start_date.timestamp()))
            offset_sec = timezone_info['rawOffset'] + timezone_info.get('dstOffset', 0)
        except Exception as e:
            return {"error": f"Failed to get time zone information: {str(e)}"}, 500

        # 일출 및 일몰 시간 계산 (여러 날짜에 대해 한 번에)
        try:
            sunrise_sunset_data = calculate_sunrise_sunset_for_range(latitude, longitude, start_date, end_date,
                                                                     offset_sec)
            return {
                "location": {"latitude": latitude, "longitude": longitude},
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d'),
                "sunrise_sunset": sunrise_sunset_data
            }, 200
        except Exception as e:
            return {"error": f"Failed to calculate sunrise and sunset times: {str(e)}"}, 500


# Blueprint와 API 설정 - Sunrise and Sunset 관련으로 명확하게 변경
sunrise_sunset_blueprint = Blueprint('sunrise_sunset', __name__)
api = Api(sunrise_sunset_blueprint, version='1.0', title='Sunrise Sunset API',
          description='API Documentation for Sunrise and Sunset Operations',doc='/api/docs')
api.add_namespace(ns)
