# meteor_shower_routes.py

# meteor_shower_routes.py

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_restx import Api, Resource, Namespace

from app.services.comets import meteor_shower_visibility_service
from app.services.comets.meteor_shower_info import get_meteor_shower_info
from app.services.comets.meteor_shower_info_storage_service import update_meteor_shower_data

# Namespace 생성
ns = Namespace('api/meteor_shower', description='Meteor Shower-related operations')


def validate_params(required_params):
    """
    매개변수를 검증하는 유틸리티 함수.
    """
    try:
        params = {}
        for param in required_params:
            value = request.args.get(param['name'], type=param.get('type', str))
            if param.get('required', True) and value is None:
                return None, {"error": f"Missing required parameter: {param['name']}"}, 400
            params[param['name']] = value
        return params, None, None
    except ValueError:
        return None, {"error": "Invalid parameter format"}, 400


@ns.route('/info')
class MeteorShowerResource(Resource):
    @staticmethod
    @ns.doc(params={
        'comet': {'description': 'Name of the comet (required). Examples: Tuttle, Swift-Tuttle, Halley'},
        'start_date': {'description': 'Start date for the meteor shower information in YYYY-MM-DD format (required)'},
        'range_days': {'description': 'Range of days to retrieve information, default is 365 (optional)'}
    })
    @ns.response(200, 'Success')
    @ns.response(400, 'Invalid input format or missing parameters.')
    @ns.response(500, 'Internal server error.')
    def get():
        """
        혜성 이름과 접근 이벤트 정보를 바탕으로 유성우 정보를 반환하는 API 엔드포인트.

        쿼리 파라미터:
            - comet (str): 혜성 이름.
                          예시: Tuttle, Swift-Tuttle, Halley
            - start_date (str): 유성우 정보를 위한 시작 날짜 (YYYY-MM-DD 형식).
                                예시: 2024-10-01
            - range_days (int, 선택): 유성우 정보를 가져올 기간 (일수), 기본값은 365일.

        반환값:
            JSON: 유성우 정보 또는 오류 메시지.
        """

        required_params = [
            {'name': 'comet', 'type': str, 'required': True},
            {'name': 'start_date', 'type': str, 'required':True},
            {'name': 'range_days', 'type': int, 'required': False}
        ]

        params, error_response, status_code = validate_params(required_params)
        if error_response:
            return error_response, status_code

        comet_name = params['comet']
        start_date_str = params['start_date']
        range_days = params.get('range_days', 365)

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD."}, 400

        try:
            meteor_shower_info = get_meteor_shower_info(comet_name, start_date.strftime('%Y-%m-%d'), range_days)
            return meteor_shower_info, 200
        except Exception as e:
            logging.error(f"Failed to get meteor shower information: {str(e)}")
            return {"error": f"Failed to get meteor shower information: {str(e)}"}, 500


@ns.route('/update')
class UpdateMeteorRawDataResource(Resource):
    @staticmethod
    @ns.response(200, 'Meteor shower data updated successfully.')
    @ns.response(500, 'Internal server error.')
    def post():
        """
        유성우 데이터를 업데이트하는 엔드포인트.
        """
        try:
            update_meteor_shower_data()
            return {"message": "Meteor shower data updated successfully."}, 200
        except Exception as e:
            logging.error(f"Failed to update meteor shower data: {str(e)}")
            return {"error": str(e)}, 500


@ns.route('/visibility')
class MeteorShowerVisibilityResource(Resource):
    @staticmethod
    @ns.doc(params={
        'name': 'Name of the meteor shower (required), EX.(Eta Aquariid, Orionid, Ursid, Perseid)',
        'year': 'Year for evaluating the meteor shower visibility (required) EX(2023, 2024)',
        'latitude': 'Latitude of the observation location (required)',
        'longitude': 'Longitude of the observation location (required)'
    })
    @ns.response(200, 'Success')
    @ns.response(400, 'Invalid input format or missing parameters.')
    @ns.response(500, 'Internal server error.')
    def get():
        """
        유성우 가시성 평가 API 엔드포인트

        사용자가 요청한 유성우의 이름, 관측 연도, 위도, 경도 정보를 바탕으로 해당 유성우의 가시성을 평가합니다.

        쿼리 파라미터:
            - name (str): 유성우 이름 (필수).
                         예시: Eta Aquariid, Orionid, Ursid, Perseid
            - year (int): 유성우 가시성을 평가할 연도 (필수).
                         예시: 2023, 2024
            - latitude (float): 관측 위치의 위도 (필수).
            - longitude (float): 관측 위치의 경도 (필수).

        반환값:
            JSON: 요청된 유성우의 가시성 데이터 또는 오류 발생 시 오류 메시지.
        """

        required_params = [
            {'name': 'name', 'type': str, 'required': True},
            {'name': 'year', 'type': int, 'required': True},
            {'name': 'latitude', 'type': float, 'required': True},
            {'name': 'longitude', 'type': float, 'required': True}
        ]

        params, error_response, status_code = validate_params(required_params)
        if error_response:
            return error_response, status_code

        name = params['name']
        year = params['year']
        latitude = params['latitude']
        longitude = params['longitude']

        try:
            data = meteor_shower_visibility_service.evaluate_meteor_shower_visibility(name, year, latitude, longitude)
            if "error" in data:
                return data, 404
            return data, 200
        except Exception as e:
            logging.error(f"Failed to evaluate meteor shower visibility: {str(e)}")
            return {"error": f"Failed to evaluate meteor shower visibility: {str(e)}"}, 500


# Blueprint와 API 설정
meteor_shower_blueprint = Blueprint('meteor_shower', __name__)
api = Api(meteor_shower_blueprint, version='1.0', title='Meteor Shower API',
          description='API Documentation for Meteor Shower Operations', doc='/api/docs')
api.add_namespace(ns)
