from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import user as user_crud
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()

# Bearer 토큰 인증 스키마 설정
security = HTTPBearer()

# JWT 토큰 설정
SECRET_KEY = os.getenv("SECRET_KEY")  # JWT 서명에 사용할 비밀키
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")  # JWT 서명 알고리즘
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))  # 토큰 만료 시간

# 데이터베이스 세션 생성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# JWT 액세스 토큰 생성 함수
def create_access_token(data: dict):
    to_encode = data.copy()
    # sub 필드를 문자열로 변환
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    
    # 토큰 만료 시간 설정
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # JWT 토큰 생성
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 현재 인증된 사용자 정보를 가져오는 함수
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    # 인증 실패 시 예외 설정
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Bearer 토큰에서 실제 토큰 값 추출
        token = credentials.credentials
        if token.startswith("Bearer "):
            token = token[7:]
        
        # 토큰 디코딩 및 검증
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 사용자 ID 추출
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # 데이터베이스에서 사용자 조회
    user = user_crud.get_user(db, user_id)
    if user is None:
        raise credentials_exception
    
    return user 