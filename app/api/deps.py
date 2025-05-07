from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.core import get_db
from app.crud import get_user_by_firebase_uid
from app.schemas import ProfileOut
from firebase_admin import auth as firebase_auth
from firebase_admin.exceptions import FirebaseError

# Bearer 토큰 인증 스키마 생성
security = HTTPBearer()

# 현재 인증된 사용자 정보를 가져오는 의존성 함수
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> ProfileOut:
    try:
        # Firebase 토큰 검증
        token = credentials.credentials
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No token provided"
            )
        
        # Bearer 접두사가 있다면 제거
        if token.startswith('Bearer '):
            token = token[7:]
        
        # 토큰이 문자열인지 확인
        if not isinstance(token, str):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format: token must be a string"
            )
        
        try:
            decoded_token = firebase_auth.verify_id_token(token)
        except FirebaseError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
        
        firebase_uid = decoded_token.get("uid")
        if not firebase_uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no uid found"
            )
        
        # Firebase UID로 사용자 조회
        user = get_user_by_firebase_uid(db, firebase_uid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
   
        return ProfileOut.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}"
        ) 