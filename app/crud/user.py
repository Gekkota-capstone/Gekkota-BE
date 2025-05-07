from sqlalchemy.orm import Session
from app.models import User
from app.schemas import ProfileCreate, ProfileUpdate
from firebase_admin import auth as firebase_auth
from firebase_admin.exceptions import FirebaseError
import base64

def extract_token(auth_header: str) -> str:
    # Bearer 토큰에서 Firebase 토큰 값을 추출
    try:
        if not auth_header.startswith('Bearer '):
            raise ValueError("Authorization header must start with 'Bearer '")
        return auth_header.split(' ')[1]
    except Exception as e:
        raise ValueError("Invalid authorization header format")

def is_valid_jwt_format(token: str) -> bool:
    # Firebase 토큰 형식이 올바른지 확인
    try:
        # Firebase 토큰은 JWT 형식 (header.payload.signature)
        parts = token.split('.')
        if len(parts) != 3:
            return False
        
        # 각 부분이 base64로 디코딩 가능한지 확인
        for part in parts:
            # base64 패딩 추가
            part += '=' * ((4 - len(part) % 4) % 4)
            try:
                base64.b64decode(part)
            except Exception:
                return False
        return True
    except Exception:
        return False
    

# Firebase UID로 사용자 조회
def get_user_by_firebase_uid(db: Session, firebase_uid: str):
    result = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    return result

# 프로필 등록
def create_profile(db: Session, auth_header: str, profile: ProfileCreate):
    try:
        # Bearer 토큰에서 실제 토큰 추출
        token = extract_token(auth_header)
        
        # 토큰 형식 검증
        if not is_valid_jwt_format(token):
            raise ValueError("Invalid token format: Token must be a valid JWT")
        
        # Firebase 토큰 검증
        try:
            decoded_token = firebase_auth.verify_id_token(token)
        except FirebaseError as e:
            raise ValueError(f"Invalid Firebase token: {str(e)}")
        except Exception as e:
            raise ValueError(f"Token verification failed: {str(e)}")
        
        # 토큰에서 필요한 정보 추출
        firebase_uid = decoded_token.get('uid')
        if not firebase_uid:
            raise ValueError("No UID found in token")
            
        email = decoded_token.get('email')
        
        # 이미 존재하는 사용자인지 확인
        existing_user = get_user_by_firebase_uid(db, firebase_uid)
        if existing_user:
            return None
        
        # 새 사용자 생성
        db_user = User(
            firebase_uid=firebase_uid,
            email=email,
            nickname=profile.nickname,
            profile=profile.profile
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except ValueError as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise ValueError(f"Failed to create profile: {str(e)}")

# 프로필 수정
def update_profile(db: Session, user_id: int, profile: ProfileUpdate):
    result = db.query(User).filter(User.id == user_id).first()
    db_user = result
    if not db_user:
        return None
    
    # 업데이트할 필드만 수정
    if profile.nickname is not None:
        db_user.nickname = profile.nickname
    if profile.profile is not None:
        db_user.profile = profile.profile
    
    db.commit()
    db.refresh(db_user)
    return db_user

# 프로필 조회
def get_profile(db: Session, user_id: int):
    result = db.query(User).filter(User.id == user_id).first()
    return result
