from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core import get_db
from app.crud import create_profile, update_profile, get_profile, get_user_by_firebase_uid, extract_token
from app.schemas import ProfileCreate, ProfileUpdate, ProfileOut
from app.api import get_current_user
from firebase_admin import auth as firebase_auth

# Bearer 토큰 인증 스키마 생성
security = HTTPBearer()

# 사용자 관련 라우터 생성 (prefix: /users, 태그: users)
router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# 프로필 등록 엔드포인트 (POST /users/profile)
@router.post("/profile", response_model=ProfileOut)
def create_profile_endpoint(
    profile: ProfileCreate,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db)
):
    try:
        # 프로필 생성
        user = create_profile(db, credentials.credentials, profile)
        if not user:
            # 이미 존재하는 사용자인 경우 해당 사용자 정보 반환
            token = extract_token(credentials.credentials)
            decoded_token = firebase_auth.verify_id_token(token)
            firebase_uid = decoded_token.get('uid')
            existing_user = get_user_by_firebase_uid(db, firebase_uid)
            return existing_user
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

# 프로필 수정 엔드포인트 (PATCH /users/me/profile)
@router.patch("/me/profile", response_model=ProfileOut)
def update_profile_endpoint(
    profile: ProfileUpdate,
    current_user: ProfileOut = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user = update_profile(db, current_user.id, profile)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

# 프로필 조회 엔드포인트 (GET /users/me/profile)
@router.get("/me/profile", response_model=ProfileOut)
def get_profile_endpoint(
    current_user: ProfileOut = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user = get_profile(db, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user