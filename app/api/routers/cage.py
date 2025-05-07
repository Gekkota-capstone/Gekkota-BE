from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core import get_db
from app.crud import create_cage, update_cage, get_cage, delete_cage, update_cleaning_cycle, get_user_cages
from app.schemas import CageCreate, CageUpdate, CageOut, CleaningCycleUpdate, ProfileOut, CageListResponse, CageStateResponse
from app.api import get_current_user

# 케이지 관련 라우터 생성 (prefix: /cages, 태그: cages)
router = APIRouter(prefix="/cages", tags=["cages"])

# 사용자의 모든 케이지 조회 엔드포인트 (GET /cages)
@router.get("", response_model=CageListResponse)
def get_cages(
    db: Session = Depends(get_db),
    current_user: ProfileOut = Depends(get_current_user)
):
    # 현재 사용자의 모든 케이지 정보 반환
    cages = get_user_cages(db, current_user.id)
    return {"list": cages}

# 새로운 케이지 생성 엔드포인트 (POST /cages)
@router.post("", response_model=CageOut)
def create_new_cage(
    cage_data: CageCreate,
    db: Session = Depends(get_db),
    current_user: ProfileOut = Depends(get_current_user)
):
    # 새로운 케이지 생성 및 반환
    return create_cage(db, current_user.id, cage_data)

# 케이지 정보 업데이트 엔드포인트 (PATCH /cages/{cage_id})
@router.patch("/{cage_id}", response_model=CageOut)
def update_cage_info(
    cage_id: int,
    update: CageUpdate,
    db: Session = Depends(get_db),
    current_user: ProfileOut = Depends(get_current_user)
):
    # 케이지 존재 여부 및 소유권 확인
    cage = get_cage(db, cage_id)
    if not cage or cage.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Cage not found")
    
    # 케이지 정보 업데이트
    updated = update_cage(db, cage_id, update)
    if not updated:
        raise HTTPException(status_code=404, detail="Cage not found")
    return updated

# 케이지 삭제 엔드포인트 (DELETE /cages/{cage_id})
@router.delete("/{cage_id}")
def delete_cage_info(
    cage_id: int,
    db: Session = Depends(get_db),
    current_user: ProfileOut = Depends(get_current_user)
):
    # 케이지 존재 여부 및 소유권 확인
    cage = get_cage(db, cage_id)
    if not cage or cage.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Cage not found")
    
    # 케이지 삭제
    delete_cage(db, cage_id)
    return {"message": "Cage deleted successfully"}

# 케이지 청소 주기 설정 엔드포인트 (PATCH /cages/{cage_id}/cleaning-cycle)
@router.patch("/{cage_id}/cleaning-cycle")
def set_cleaning_cycle(
    cage_id: int,
    cycle: CleaningCycleUpdate,
    db: Session = Depends(get_db),
    current_user: ProfileOut = Depends(get_current_user)
):
    # 케이지 존재 여부 및 소유권 확인
    cage = get_cage(db, cage_id)
    if not cage or cage.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Cage not found")
    
    # 청소 주기 업데이트
    updated = update_cleaning_cycle(db, cage_id, cycle)
    if not updated:
        raise HTTPException(status_code=404, detail="Cage not found")
    return updated

# 케이지 상태 조회 엔드포인트 (GET /cages/{cage_id}/state)
@router.get("/{cage_id}/state", response_model=CageStateResponse)
def get_cage_state(
    cage_id: int,
    db: Session = Depends(get_db),
    current_user: ProfileOut = Depends(get_current_user)
):
    # 케이지 존재 여부 및 소유권 확인
    cage = get_cage(db, cage_id)
    if not cage or cage.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Cage not found")
    
    # 케이지 상태 반환
    return {"state": cage.state if cage.state else ""}