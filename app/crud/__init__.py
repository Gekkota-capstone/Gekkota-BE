# 사용자 관련 CRUD 작업 함수들을 import
from .user import (
    create_profile,          # 프로필 생성
    update_profile,          # 프로필 수정
    get_profile,            # 프로필 조회
    get_user_by_firebase_uid,# Firebase UID로 사용자 조회
    extract_token           # 토큰 추출
)

# 케이지 관련 CRUD 작업 함수들을 import
from .cage import (
    get_cage,           # 케이지 조회
    get_user_cages,     # 사용자의 케이지 목록 조회
    create_cage,        # 케이지 생성
    update_cage,        # 케이지 수정
    delete_cage         # 케이지 삭제
)

# 청소 관련 CRUD 작업 함수들을 import
from .cleaning import (
    create_cleaning_record,         # 청소 기록 생성
    get_cleaning_records_by_cage,   # 케이지별 청소 기록 조회
    delete_cleaning_record,         # 청소 기록 삭제
    update_cleaning_cycle           # 청소 주기 업데이트
)

# 건강 관련 CRUD 작업 함수들을 import
from .health import (
    create_health_record,           # 건강 기록 생성
    get_health_records_by_cage,     # 케이지별 건강 기록 조회
    delete_health_record            # 건강 기록 삭제
)

# 급여 관련 CRUD 작업 함수들을 import
from .feeding import (
    create_feeding_record,          # 급여 기록 생성
    get_feeding_records_by_cage,    # 케이지별 급여 기록 조회
    delete_feeding_record           # 급여 기록 삭제
)

# 활동 관련 CRUD 작업 함수들을 import
from .activity import (
    get_activity_by_camera_id       # 카메라 ID로 활동 기록 조회
)

# 카메라 관련 CRUD 작업 함수들을 import
from .camera import (
    get_camera_data_by_cage         # 케이지별 카메라 데이터 조회
)

# 이 모듈에서 외부로 노출할 이름들을 정의
# from app.crud import * 를 사용할 때 이 목록에 있는 것들만 import됨
__all__ = [
    # User 관련 함수들
    "create_profile", "update_profile", "get_profile",
    "get_user_by_firebase_uid", "extract_token",
    
    # Cage 관련 함수들
    "get_cage", "get_user_cages", "create_cage", "update_cage", "delete_cage",
    
    # Cleaning 관련 함수들
    "create_cleaning_record", "get_cleaning_records_by_cage",
    "delete_cleaning_record", "update_cleaning_cycle",
    
    # Health 관련 함수들
    "create_health_record", "get_health_records_by_cage", "delete_health_record",
    
    # Feeding 관련 함수들
    "create_feeding_record", "get_feeding_records_by_cage", "delete_feeding_record",
    
    # Activity 관련 함수들
    "get_activity_by_camera_id",
    
    # Camera 관련 함수들
    "get_camera_data_by_cage"
]
