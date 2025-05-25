# /util/firebase_util.py

import os
import firebase_admin
from firebase_admin import auth, credentials
from fastapi import HTTPException, status, Depends, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from util.config_util import is_test_mode

# Firebase 초기화 (테스트 모드가 아닌 경우에만)
if not is_test_mode():
    try:
        firebase_app = firebase_admin.get_app()
    except ValueError:
        # 서비스 계정 키 파일 경로 설정 (실제 환경에 맞게 조정 필요)
        cred = credentials.Certificate(os.getenv("FIREBASE_ADMIN_CREDENTIAL_JSON"))
        firebase_app = firebase_admin.initialize_app(cred)

# 테스트 모드에서는 auto_error를 False로 설정하여 토큰 없이도 요청 허용
security = HTTPBearer(auto_error=not is_test_mode())


async def verify_firebase_token(
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        x_firebase_uid: str = Header(None, description="테스트용 Firebase UID (테스트 모드에서만 사용)")
):
    """
    Firebase 토큰을 검증하거나 테스트 모드에서 X-Firebase-UID 헤더를 확인합니다.
    """
    if is_test_mode():
        # 테스트 모드에서는 X-Firebase-UID 헤더에서 직접 uid를 가져옴
        if x_firebase_uid:
            return {"uid": x_firebase_uid}
        # Bearer 토큰이 있으면 사용 시도 (선택적)
        elif credentials:
            try:
                decoded_token = auth.verify_id_token(credentials.credentials)
                return decoded_token
            except Exception:
                # 테스트 모드에서는 토큰 검증 실패해도 기본값 사용
                pass
        # 기본 테스트 uid 반환
        return {"uid": "test-user-id"}

    # 프로덕션 모드: 실제 Firebase 토큰 검증
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_firebase_uid(token_data: dict = Depends(verify_firebase_token)):
    """
    인증된 사용자의 Firebase UID를 반환합니다.
    """
    firebase_uid = token_data.get("uid")
    if not firebase_uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return firebase_uid