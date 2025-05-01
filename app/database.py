import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()  # .env 파일에서 환경 변수 로드

# 데이터베이스 연결 정보를 환경 변수에서 가져옴
DB_USER = os.getenv("DB_USER")  # 데이터베이스 사용자 이름
DB_PASSWORD = os.getenv("DB_PASSWORD")  # 데이터베이스 비밀번호
DB_HOST = os.getenv("DB_HOST")  # 데이터베이스 호스트 주소
DB_PORT = os.getenv("DB_PORT")  # 데이터베이스 포트 번호
DB_NAME = os.getenv("DB_NAME")  # 데이터베이스 이름

# MySQL 데이터베이스 연결 URL 생성
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# 데이터베이스 엔진 생성
# pool_pre_ping=True: 연결이 끊어졌을 때 자동으로 재연결
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# 데이터베이스 세션 팩토리 생성
# autocommit=False: 자동 커밋 비활성화
# autoflush=False: 자동 플러시 비활성화
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy 모델의 기본 클래스 생성
Base = declarative_base()