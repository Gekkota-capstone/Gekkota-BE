from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserOut
from app.database import SessionLocal
from app.crud import user as user_crud

# 인증 관련 라우터 생성 (prefix: /auth, 태그: auth)
router = APIRouter(prefix="/auth", tags=["auth"])

# 데이터베이스 세션 의존성 함수
def get_db():
    # 새로운 데이터베이스 세션 생성
    db = SessionLocal()
    try:
        # 세션을 yield하여 라우터에서 사용할 수 있게 함
        yield db
    finally:
        # 요청 처리가 끝나면 세션을 닫음
        db.close()

# 구글 로그인 엔드포인트 (POST /auth/google-login)
@router.post("/google-login", response_model=UserOut)
def google_login(user_data: UserCreate, db: Session = Depends(get_db)):
    # 구글 토큰으로 사용자 조회
    user = user_crud.get_user_by_token(db, user_data.google_token)
    # 사용자가 존재하지 않으면 새로 생성
    if not user:
        user = user_crud.create_user(db, user_data)
    # 사용자 정보 반환
    return user