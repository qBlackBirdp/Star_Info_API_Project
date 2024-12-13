# # db_utils.py
#
# import logging
# import time
# from contextlib import contextmanager
# from sqlalchemy.exc import OperationalError
# from app.db.session_manager import Session
#
#
# def retry_query(session, query, retries=3, delay=5):
#     """
#     데이터베이스 쿼리를 재시도하는 함수
#
#     Args:
#         session: SQLAlchemy 세션
#         query: 실행할 쿼리
#         retries: 재시도 횟수
#         delay: 재시도 전 대기 시간 (초 단위)
#
#     Returns:
#         쿼리 결과 또는 예외 발생 시 None 반환
#     """
#     for i in range(retries):
#         try:
#             return query.all()
#         except OperationalError as e:
#             if i < retries - 1:
#                 logging.warning(f"Query failed with error: {e}. Retrying in {delay} seconds...")
#                 time.sleep(delay)
#             else:
#                 logging.error(f"All retries failed for query: {e}")
#                 return None
#
#
# @contextmanager
# def get_session():
#     """
#     Flask 애플리케이션 컨텍스트에서 데이터베이스 세션을 안전하게 가져오는 컨텍스트 매니저
#     """
#     if not Session:
#         raise RuntimeError("Session is not initialized. Ensure the application context is active.")
#     try:
#         yield Session
#     finally:
#         Session.remove()  # 세션 정리


############################################

import logging
import time
from contextlib import contextmanager
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import scoped_session, sessionmaker
from app.db.session_manager import mariadb_engine, postgres_engine


def retry_query(session, query, retries=3, delay=5):
    """
    데이터베이스 쿼리를 재시도하는 함수

    Args:
        session: SQLAlchemy 세션
        query: 실행할 쿼리
        retries: 재시도 횟수
        delay: 재시도 전 대기 시간 (초 단위)

    Returns:
        쿼리 결과 또는 예외 발생 시 None 반환
    """
    for i in range(retries):
        try:
            return query.all()
        except OperationalError as e:
            if i < retries - 1:
                logging.warning(f"Query failed with error: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logging.error(f"All retries failed for query: {e}")
                return None


@contextmanager
def get_session(db_type):
    """
    데이터베이스 유형에 따라 SQLAlchemy 세션을 안전하게 가져오는 컨텍스트 매니저

    Args:
        db_type: 사용할 데이터베이스 유형 ("mariadb" 또는 "postgres")

    Yields:
        SQLAlchemy 세션 객체
    """
    if db_type == "mariadb":
        engine = mariadb_engine
    elif db_type == "postgres":
        engine = postgres_engine
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

    session = scoped_session(sessionmaker(bind=engine))
    try:
        yield session
    finally:
        session.remove()  # 세션 정리
