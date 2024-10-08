# 모든 API 엔드포인트 정의

from flask import Blueprint, jsonify

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return "Welcome to the Star Info API!"

@main.route('/api/meteors/<string:shower_name>')
def get_meteor_shower(shower_name):
    # 여기서 유성우 정보 처리
    return jsonify({
        "meteor_shower": shower_name.capitalize(),
        "message": "This is a test response."
    })
