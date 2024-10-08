from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/starinfo', methods=['GET'])
def get_star_info():
    # 샘플 데이터: 특정 별에 대한 정보
    star_data = {
        'name': 'Sirius',
        'constellation': 'Canis Major',
        'distance_light_years': 8.6
    }
    return jsonify(star_data)

if __name__ == '__main__':
    app.run(debug=True)
