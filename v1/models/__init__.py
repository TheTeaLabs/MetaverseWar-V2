"""데이터베이스 설정"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from env import DB_ID, DB_PW, DB_URL, DB_PORT, DB_DB

SQLALCHEMY_DATABASE_URL = f'mysql+mysqlconnector://{DB_ID}:{DB_PW}@{DB_URL}:{DB_PORT}/{DB_DB}?charset=utf8mb4'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = session_local()

Base = declarative_base()


def get_db():
    """db 객체 반환"""
    session = session_local()
    try:
        yield session
        session.commit()
    finally:
        session.close()
