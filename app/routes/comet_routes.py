# comet_routes.py

# comet_routes.py

from datetime import datetime
from flask import request, Blueprint
from flask_restx import Api, Resource, Namespace
from app.services.comets.comet_approach_service import get_comet_approach_data

# Namespace 생성
ns = Namespace('api/comet', description='Comet-related operations')


@ns.route('/approach')
class CometApproachResource(Resource):
    @staticmethod
    @ns.doc(params={
        'comet': {
            'description': 'Name of the comet for which you want approach information (required)',
            'required': True,
            'example': 'Tuttle'
        },
        'start_date': {
            'description': 'Start date for the comet approach information in YYYY-MM-DD format (required)',
            'required': True,
            'example': '2024-10-01'
        },
        'range_days': {
            'description': 'Number of days to consider for approach information (optional, default is 365)',
            'required': False,
            'example': 365
        }
    })
    @ns.response(200, 'Success')
    @ns.response(400, 'Invalid input format or missing parameters.')
    @ns.response(500, 'Internal server error.')
    def get():
        """
        사용자가 요청한 혜성 접근 이벤트 정보를 반환하는 API 엔드포인트

        쿼리 파라미터:
            - comet (str): 혜성의 이름 (필수).
                          예시: Tuttle, Swift-Tuttle, Halley.
            - start_date (str): 접근 정보를 위한 시작 날짜 (필수).
                               형식: YYYY-MM-DD. 예시: 2024-10-01.
            - range_days (int, 선택): 접근 정보를 고려할 일 수.
                                     기본값은 365일. 예시: 365.

        반환값:
            JSON: 혜성 접근 이벤트 정보 또는 오류 메시지.
        """

        comet_name = request.args.get('comet')
        start_date_str = request.args.get('start_date')
        range_days = request.args.get('range_days', type=int, default=365)
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)

        # 필수 매개변수 검증
        if not comet_name or not start_date_str:
            return {"error": "Missing required parameters: 'comet' and 'start_date' are required."}, 400

        # 날짜 문자열을 datetime 객체로 변환
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD."}, 400

        try:
            # 혜성 접근 이벤트 데이터 가져오기
            result = get_comet_approach_data(comet_name, start_date.strftime('%Y-%m-%d'), range_days)
            return result, 200
        except Exception as e:
            return {"error": f"Failed to get comet approach: {str(e)}"}, 500


# Blueprint와 API 설정
comet_blueprint = Blueprint('comet', __name__)
api = Api(comet_blueprint, version='1.0', title='Comet API', description='API Documentation for Comet Operations',
          doc='/api/docs')
api.add_namespace(ns)
