# Flask 앱 초기화

from flask import Flask, Blueprint
from flask_caching import Cache
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

from app.db.session_manager import Session

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
    app.config['CACHE_REDIS_PORT'] = 6379               # Redis 서버 포트
    app.config['CACHE_REDIS_DB'] = 1                    # Redis DB 인덱스 (기본: 0)
    app.config['CACHE_DEFAULT_TIMEOUT'] = 1000          # 캐싱 데이터의 기본 유효 기간 (초)

    # 캐싱 초기화
    cache.init_app(app)

    # 앱 설정
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@mysql_container:3306/STAR_INFO_API_DB'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # SQLAlchemy 엔진 최적화 설정
    db_engine = create_engine(
        app.config['SQLALCHEMY_DATABASE_URI'],
        pool_size=50,            # 기본 연결 수
        max_overflow=100,         # 최대 초과 연결 수
        pool_timeout=60,
        pool_pre_ping=True       # 끊어진 연결 확인
    )

    # SQLAlchemy 및 Migrate 초기화
    db.init_app(app)
    migrate.init_app(app, db)

    # Session 바인딩
    with app.app_context():
        Session.configure(bind=db_engine)

    # 기존 API 경로 유지 - Blueprint 등록
    from app.routes import main
    app.register_blueprint(main)

    return app

# app/app_factory.py

# import os
# from flask import Flask, Blueprint, g
# from flask_caching import Cache
# from flask_migrate import Migrate
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import create_engine
# from app.db.session_manager import Session
#
# # Flask-SQLAlchemy 초기화
# db = SQLAlchemy()
# migrate = Migrate()
# cache = Cache()
#
#
# def create_app():
#     """
#     Flask 애플리케이션을 생성하고 설정하는 함수
#     """
#     app = Flask(__name__)
#
#     # Flask-Caching 설정
#     app.config['CACHE_TYPE'] = 'RedisCache'
#     app.config['CACHE_REDIS_HOST'] = 'redis_container'
#     app.config['CACHE_REDIS_PORT'] = 6379
#     app.config['CACHE_REDIS_DB'] = 1
#     app.config['CACHE_DEFAULT_TIMEOUT'] = 1000
#
#     # 데이터베이스 URI 설정
#     db_type = os.getenv("DB_TYPE", "mariadb")  # 기본은 mariadb
#     if db_type == "mariadb":
#         app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@mysql_container:3306/STAR_INFO_API_DB'
#     elif db_type == "postgres":
#         app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@postgres_container:5432/STAR_INFO_API_DB'
#     else:
#         raise ValueError("Unsupported DB_TYPE. Use 'mariadb' or 'postgres'.")
#
#     # SQLAlchemy 및 Migrate 초기화
#     db.init_app(app)
#     migrate.init_app(app, db)
#
#     # Flask-Caching 초기화
#     cache.init_app(app)
#
#     # 애플리케이션 컨텍스트에서 세션 바인딩
#     mariadb_engine = create_engine(
#         'mysql+pymysql://root:1234@mysql_container:3306/STAR_INFO_API_DB',
#         pool_size=20,            # 기본 Connection Pool 크기 (기본값: 5)
#         max_overflow=30,         # 추가로 허용되는 연결 수 (기본값: 10)
#         pool_timeout=60,         # 연결 대기 시간 (기본값: 30초)
#         pool_recycle=1800        # 연결 재활용 시간 (기본값: 없음)
#     )
#     postgres_engine = create_engine(
#         'postgresql://postgres:1234@postgres_container:5432/STAR_INFO_API_DB',
#         pool_size=20,            # 기본 Connection Pool 크기 (기본값: 5)
#         max_overflow=30,         # 추가로 허용되는 연결 수 (기본값: 10)
#         pool_timeout=60,         # 연결 대기 시간 (기본값: 30초)
#         pool_recycle=1800        # 연결 재활용 시간 (기본값: 없음)
#     )
#
#     @app.before_request
#     def bind_session():
#         """
#         요청 전에 세션을 적절한 엔진에 바인딩
#         """
#         db_type = os.getenv("DB_TYPE", "mariadb")  # 기본은 mariadb
#         if db_type == "mariadb":
#             Session.configure(bind=mariadb_engine)
#         elif db_type == "postgres":
#             Session.configure(bind=postgres_engine)
#
#     @app.teardown_request
#     def remove_session(exception=None):
#         """
#         요청이 끝난 후 세션 정리
#         """
#         Session.remove()
#
#     # 기존 API 경로 유지 - Blueprint 등록
#     from app.routes import main
#     app.register_blueprint(main)
#
#     return app
