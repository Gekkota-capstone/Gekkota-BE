from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

# Google 토큰으로 사용자 조회
def get_user_by_token(db: Session, token: str):
    return db.query(User).filter(User.google_token == token).first()

# 새로운 사용자 생성
def create_user(db: Session, user_create: UserCreate):
    user = User(google_token=user_create.google_token)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# 사용자 닉네임 업데이트
def update_nickname(db: Session, user_id: int, new_nickname: str):
    # 이미 존재하는 닉네임인지 확인 (자신의 현재 닉네임은 제외)
    existing_user = db.query(User).filter(User.nickname == new_nickname).first()
    if existing_user and existing_user.id != user_id:
        return None  # 중복된 닉네임
    
    # 사용자 조회 및 닉네임 업데이트
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.nickname = new_nickname
        db.commit()
        db.refresh(user)
    return user

# 사용자 ID로 사용자 조회
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# Google ID로 사용자 조회
def get_user_by_google_id(db: Session, google_id: str):
    return db.query(User).filter(User.google_token == google_id).first()

# Google 계정으로 새로운 사용자 생성
def create_user_with_google(db: Session, google_id: str, email: str, name: str):
    # 임시 닉네임 생성 (이메일의 @ 앞부분 사용)
    nickname = email.split('@')[0]
    
    # 닉네임이 이미 존재하는 경우 숫자 추가
    base_nickname = nickname
    counter = 1
    while db.query(User).filter(User.nickname == nickname).first():
        nickname = f"{base_nickname}{counter}"
        counter += 1
    
    # 새로운 사용자 객체 생성
    db_user = User(
        google_token=google_id,
        email=email,
        name=name,
        nickname=nickname
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
