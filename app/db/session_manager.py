# session_manager.py

from sqlalchemy.orm import scoped_session, sessionmaker

# scoped_session 초기화
Session = scoped_session(sessionmaker())


#######################

# from sqlalchemy import create_engine
# from sqlalchemy.orm import scoped_session, sessionmaker
#
# # 데이터베이스 엔진 생성
# mariadb_engine = create_engine(
#     "mysql+pymysql://root:1234@mysql_container:3306/STAR_INFO_API_DB",
#     pool_size=10,
#     max_overflow=20,
#     pool_pre_ping=True
# )
#
# postgres_engine = create_engine(
#     "postgresql://postgres:1234@postgres_container:5432/STAR_INFO_API_DB",
#     pool_size=10,
#     max_overflow=20,
#     pool_pre_ping=True
# )
#
# # scoped_session 초기화
# Session = scoped_session(sessionmaker())
