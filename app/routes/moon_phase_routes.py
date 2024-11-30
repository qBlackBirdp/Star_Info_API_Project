# moon_phase_routes.py

from datetime import datetime
from flask import Blueprint, request
from flask_restx import Api, Resource, Namespace, fields

from app.services.moon_phase_service import get_moon_phase_for_date

# Namespace 생성
ns = Namespace('api/moon', description='Operations related to moon phase calculations.')

# 모델 정의 (Swagger에서 입출력 형식을 명확히 보여줄 수 있음)
moon_phase_response_model = ns.model('MoonPhaseResponse', {
    'phase_name': fields.String(description='The name of the moon phase', example='Full Moon'),
    'illumination': fields.Float(description='Illumination percentage of the moon', example=100.0)
})


# Moon Phase Resource 정의
@ns.route('/phase')
class MoonPhaseResource(Resource):
    @ns.param('date', 'The date for which you want to calculate the moon phase in YYYY-MM-DD format', required=True)
    @ns.response(200, 'Success', moon_phase_response_model)
    @ns.response(400, 'Invalid input format.')
    @ns.response(500, 'Internal server error.')
    def get(self):
        """
        특정 날짜와 위치에 대한 달의 위상을 계산하는 엔드포인트

        Query Params:
            date (str): 날짜 (YYYY-MM-DD 형식)

        Returns:
            JSON: 달의 위상 정보 또는 오류 메시지
        """
        # 쿼리 매개변수 가져오기
        date_str = request.args.get('date')

        # 필수 매개변수 체크
        if not date_str:
            return {"error": "Missing required parameter: 'date'."}, 400

        # 날짜 문자열을 datetime 객체로 변환
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD."}, 400

        try:
            # 달의 위상 계산
            moon_phase_data = get_moon_phase_for_date(date)
            return moon_phase_data, 200
        except Exception as e:
            return {"error": f"Failed to calculate moon phase: {str(e)}"}, 500


# Blueprint와 API 설정
moon_phase_blueprint = Blueprint('moon_phase', __name__)
api = Api(moon_phase_blueprint, version='1.0', title='Moon Phase API',
          description='API Documentation for Moon Phase Operations', doc='/api/docs')
api.add_namespace(ns)
