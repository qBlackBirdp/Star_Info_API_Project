# Flask 앱 초기화

from flask import Flask

def create_app():
    """
    Flask 애플리케이션을 생성하고 설정하는 함수
    """
    app = Flask(__name__)

    # Blueprint 등록
    from .routes import main
    app.register_blueprint(main)

    return app