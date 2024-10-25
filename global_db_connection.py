# # global_db_connection.py
#
# import atexit
# import logging
# from typing import Optional
# import pymysql
# from pymysql.connections import Connection
# from config_loader import load_db_config
#
# # 로깅 설정
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
#
# # 전역 DB 연결 객체
# DB_CONNECTION: Optional[Connection] = None
#
#
# def load_db_connection():
#     global DB_CONNECTION
#     if DB_CONNECTION is None:
#         try:
#             # DB 설정 로드
#             db_config = load_db_config()
#             logging.info(f"DB 설정 로드 성공: {db_config}")
#             # DB 연결 생성
#             DB_CONNECTION = pymysql.connect(**db_config)
#             logging.info("DB 연결 성공")
#         except Exception as e:
#             logging.error(f"DB 연결 실패: {e}")
#             DB_CONNECTION = None
#
#
# # 애플리케이션 시작 시 연결 로드
# load_db_connection()
#
#
# # DB 연결 객체 반환 함수
# def get_db_connection():
#     global DB_CONNECTION
#     try:
#         # 커넥션이 유효한지 확인하고, 끊어진 경우 재연결 시도
#         if DB_CONNECTION is None or not DB_CONNECTION.open:
#             logging.warning("DB 연결이 끊어졌습니다. 재연결 시도 중...")
#             load_db_connection()
#
#         # 유효성 검사 - 커넥션 핑
#         DB_CONNECTION.ping(reconnect=True)
#
#     except Exception as e:
#         logging.error(f"DB 재연결 시도 중 오류 발생: {e}")
#         DB_CONNECTION = None
#
#     return DB_CONNECTION
#
#
# def close_db_connection():
#     global DB_CONNECTION
#     if DB_CONNECTION is not None:
#         DB_CONNECTION.close()
#         logging.info("DB 연결 해제 성공")
#         DB_CONNECTION = None
#
#
# atexit.register(close_db_connection)
