# session_manager.py

from sqlalchemy.orm import scoped_session, sessionmaker

# scoped_session 초기화
Session = scoped_session(sessionmaker())
