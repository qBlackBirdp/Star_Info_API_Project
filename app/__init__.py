# Flask 앱 초기화

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from app.db.session_manager import Session
from flask_caching import Cache


# Flask-SQLAlchemy 초기화
db = SQLAlchemy()
migrate = Migrate()

cache = Cache()


def create_app():
    """
    Flask 애플리케이션을 생성하고 설정하는 함수
    """
    app = Flask(__name__)

    # Flask-Caching 설정
    app.config['CACHE_TYPE'] = 'RedisCache'
    app.config['CACHE_REDIS_HOST'] = 'redis_container'  # Redis 서버 호스트
    app.config['CACHE_REDIS_PORT'] = 6379         # Redis 서버 포트
    app.config['CACHE_REDIS_DB'] = 1              # Redis DB 인덱스 (기본: 0)
    app.config['CACHE_DEFAULT_TIMEOUT'] = 1000     # 캐싱 데이터의 기본 유효 기간 (초)

    # 캐싱 초기화
    cache.init_app(app)

    # 앱 설정
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@mysql_container:3306/STAR_INFO_API_DB'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # SQLAlchemy 엔진 최적화 설정
    db_engine = create_engine(
        app.config['SQLALCHEMY_DATABASE_URI'],
        pool_size=10,            # 기본 연결 수
        max_overflow=20,         # 최대 초과 연결 수
        pool_pre_ping=True       # 끊어진 연결 확인
    )

    # SQLAlchemy 및 Migrate 초기화
    db.init_app(app)
    migrate.init_app(app, db)

    # Session 바인딩
    with app.app_context():
        Session.configure(bind=db_engine)

    # Blueprint 등록
    from .routes import main
    app.register_blueprint(main)

    return app
