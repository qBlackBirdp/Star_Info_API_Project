# 모든 API 엔드포인트 정의

from flask import Blueprint, jsonify

main = Blueprint('main', __name__)

# 유성우 데이터 (정적 데이터로 정의)
meteor_showers = {
    "perseids": {
        "peak_date": "2024-08-12",
        "best_time": "02:00",
        "location": {
            "latitude": 34.0522,
            "longitude": -118.2437
        },
        "expected_rate": "60 meteors per hour"
    },
    "geminids": {
        "peak_date": "2024-12-14",
        "best_time": "03:00",
        "location": {
            "latitude": 51.5074,
            "longitude": -0.1278
        },
        "expected_rate": "120 meteors per hour"
    }
}

# 기본 라우트
@main.route('/')
def index():
    return "Welcome to the Star Info API!"

# 유성우 예보 API 라우트
@main.route('/api/meteors/<string:shower_name>', methods=['GET'])
def get_meteor_shower(shower_name):
    # 입력받은 유성우 이름을 소문자로 변환해서 데이터에서 검색
    shower = meteor_showers.get(shower_name.lower())

    # 데이터가 없을 경우 404 에러 반환
    if not shower:
        return jsonify({"error": "Meteor shower not found"}), 404
    
    # 유성우 데이터를 JSON으로 반환
    return jsonify({
        "meteor_shower": shower_name.capitalize(),
        "peak_date": shower["peak_date"],
        "best_time": shower["best_time"],
        "location": {
            "latitude": shower["location"]["latitude"],
            "longitude": shower["location"]["longitude"]
        },
        "expected_rate": shower["expected_rate"]
    })
