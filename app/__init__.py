# Flask 앱 초기화

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    """
    Flask 애플리케이션을 생성하고 설정하는 함수
    """
    app = Flask(__name__)

    # 앱 설정
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@mysql_container:3306/STAR_INFO_API_DB'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # SQLAlchemy 및 Migrate 초기화
    db.init_app(app)
    migrate.init_app(app, db)

    # 모델 import는 db 초기화 후에 수행
    from app import models

    # Blueprint 등록
    from .routes import main
    app.register_blueprint(main)

    return app
