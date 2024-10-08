# Flask 앱 초기화

from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Config 파일 불러오기 (optional)
    app.config.from_pyfile('../instance/config.py', silent=True)

    # 블루프린트 등록 (라우트 연결)
    from .routes import main
    app.register_blueprint(main)

    return app
