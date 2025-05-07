# 데이터베이스 관련 핵심 기능들을 import
# Base: SQLAlchemy 모델의 기본 클래스
# engine: 데이터베이스 연결 엔진
# get_db: 데이터베이스 세션을 가져오는 의존성 함수
from .database import Base, engine, get_db


# 이 모듈에서 외부로 노출할 이름들을 정의
# from app.core import * 를 사용할 때 이 목록에 있는 것들만 import됨
__all__ = [
    "Base",     # SQLAlchemy 모델 기본 클래스
    "engine",   # 데이터베이스 연결 엔진
    "get_db",   # DB 세션 의존성 함수
]
