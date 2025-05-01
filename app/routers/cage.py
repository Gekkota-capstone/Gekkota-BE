from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.cage import CageCreate, CageOut, CageUpdate
from app.schemas.cleaning import CleaningCycleUpdate
from app.crud.cleaning import update_cleaning_cycle
from app.crud import cage as cage_crud
from app.database import SessionLocal
from app.auth.dependencies import get_current_user
from app.schemas.user import UserOut

# 케이지 관련 라우터 생성 (prefix: /cages, 태그: cages)
router = APIRouter(prefix="/cages", tags=["cages"])

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

# 사용자의 모든 케이지 조회 엔드포인트 (GET /cages)
@router.get("", response_model=list[CageOut])
def get_cages(
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    # 현재 사용자의 모든 케이지 정보 반환
    return cage_crud.get_user_cages(db, current_user.id)

# 새로운 케이지 생성 엔드포인트 (POST /cages)
@router.post("", response_model=CageOut)
def create_cage(
    cage: CageCreate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    # 새로운 케이지 생성 및 반환
    return cage_crud.create_cage(db, current_user.id, cage)

# 케이지 정보 업데이트 엔드포인트 (PATCH /cages/{cage_id})
@router.patch("/{cage_id}", response_model=CageOut)
def update_cage(
    cage_id: int,
    update: CageUpdate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    # 케이지 존재 여부 및 소유권 확인
    cage = cage_crud.get_cage(db, cage_id)
    if not cage or cage.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Cage not found")
    
    # 케이지 정보 업데이트
    updated = cage_crud.update_cage(db, cage_id, update)
    if not updated:
        raise HTTPException(status_code=404, detail="Cage not found")
    return updated

# 케이지 삭제 엔드포인트 (DELETE /cages/{cage_id})
@router.delete("/{cage_id}", status_code=204)
def delete_cage(
    cage_id: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    # 케이지 존재 여부 및 소유권 확인
    cage = cage_crud.get_cage(db, cage_id)
    if not cage or cage.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Cage not found")
    
    # 케이지 삭제
    deleted = cage_crud.delete_cage(db, cage_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Cage not found")

# 케이지 청소 주기 설정 엔드포인트 (PATCH /cages/{cage_id}/cleaning-cycle)
@router.patch("/{cage_id}/cleaning-cycle")
def set_cleaning_cycle(
    cage_id: int,
    cycle: CleaningCycleUpdate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    # 케이지 존재 여부 및 소유권 확인
    cage = cage_crud.get_cage(db, cage_id)
    if not cage or cage.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Cage not found")
    
    # 청소 주기 업데이트
    updated = update_cleaning_cycle(db, cage_id, cycle)
    if not updated:
        raise HTTPException(status_code=404, detail="Cage not found")
    return updated