from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests
from google.auth.exceptions import GoogleAuthError
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import user as user_crud
from app.auth.dependencies import create_access_token
from dotenv import load_dotenv
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

# 인증 관련 라우터 설정
router = APIRouter(prefix="/auth", tags=["auth"])

# Google OAuth 설정
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
logger.info(f"GOOGLE_CLIENT_ID: {GOOGLE_CLIENT_ID[:5]}... (길이: {len(GOOGLE_CLIENT_ID) if GOOGLE_CLIENT_ID else 0})")

# Google 로그인 요청 데이터 모델
class GoogleLoginRequest(BaseModel):
    google_token: str

# Google 로그인 응답 데이터 모델
class GoogleLoginResponse(BaseModel):
    user_id: int
    nickname: str
    token: str

# 데이터베이스 세션 생성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Google 로그인 엔드포인트
@router.post("/google-login", response_model=GoogleLoginResponse)
async def google_login(
    request: GoogleLoginRequest,
    db: Session = Depends(get_db)
):
    try:
        # Google ID 토큰 검증
        idinfo = id_token.verify_oauth2_token(
            request.google_token, requests.Request(), GOOGLE_CLIENT_ID
        )
        logger.info(f"Google token verification successful: {idinfo}")
        
        # 사용자 정보 추출
        google_id = idinfo["sub"]
        email = idinfo["email"]
        name = idinfo.get("name", "")
        logger.info(f"Extracted user info: google_id={google_id}, email={email}, name={name}")
        
        # 데이터베이스에서 사용자 조회 또는 생성
        user = user_crud.get_user_by_google_id(db, google_id)
        if not user:
            logger.info(f"Creating new user with Google ID: {google_id}")
            user = user_crud.create_user_with_google(
                db,
                google_id=google_id,
                email=email,
                name=name
            )
        else:
            logger.info(f"Found existing user: {user.id}, {user.nickname}")
        
        # JWT 토큰 생성
        access_token = create_access_token(data={"sub": user.id})
        logger.info(f"Created JWT token: {access_token[:10]}... (길이: {len(access_token)})")
        
        return GoogleLoginResponse(
            user_id=user.id,
            nickname=user.nickname,
            token=access_token
        )
        
    except GoogleAuthError as e:
        logger.error(f"Google authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )
    except Exception as e:
        logger.error(f"Unexpected error during Google login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google login failed: {str(e)}"
        ) 