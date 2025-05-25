# /service/pet_health_service.py

from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Dict, Any, Optional
from repository.pet_health_repository import PetHealthRepository
from repository.entity.pet_health_entity import PetHealth
from datetime import date, datetime
import calendar


class PetHealthService:
    def __init__(self):
        self.repository = PetHealthRepository()

    def create_pet_health(self, db: Session, firebase_uid: str, pet_id: str, health_date: date,
                          weight: Optional[float] = None, memo: Optional[str] = None,
                          shedding_status: Optional[str] = None) -> Dict[str, Any]:
        pet_health = self.repository.create(db, firebase_uid, pet_id, health_date,
                                            weight, memo, shedding_status)
        return self._pet_health_to_dict(pet_health)

    def get_pet_health(self, db: Session, firebase_uid: str, pet_id: str,
                       health_date: date) -> Dict[str, Any]:
        pet_health = self.repository.get(db, firebase_uid, pet_id, health_date)

        # 기본 정보 가져오기
        if pet_health:
            result = self._pet_health_to_dict(pet_health)
        else:
            # 레코드가 없는 경우에도 기본 구조를 생성
            result = {
                "pet_id": pet_id,
                "date": health_date.isoformat(),
                "weight": None,
                "memo": None,
                "shedding_status": None,
                "monthOfWeight": [],
                "yearOfWeight": []
            }

        # 해당 월의 일별 체중 데이터 추가
        result["monthOfWeight"] = self._get_monthly_weight_stats(db, pet_id, health_date)

        # 해당 연도의 월별 체중 데이터 추가
        result["yearOfWeight"] = self._get_yearly_weight_stats(db, pet_id, health_date)

        return result

    def get_pet_healths_by_date_range(self, db: Session, pet_id: str,
                                      start_date: date, end_date: date) -> List[Dict[str, Any]]:
        pet_healths = self.repository.get_by_date_range(db, pet_id, start_date, end_date)
        return [self._pet_health_to_dict(pet_health) for pet_health in pet_healths]

    def update_pet_health(self, db: Session, firebase_uid: str, pet_id: str,
                          health_date: date, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pet_health = self.repository.update(db, firebase_uid, pet_id, health_date, **data)
        if not pet_health:
            return None
        return self._pet_health_to_dict(pet_health)

    def delete_pet_health(self, db: Session, firebase_uid: str, pet_id: str, health_date: date) -> bool:
        return self.repository.delete(db, firebase_uid, pet_id, health_date)

    def _pet_health_to_dict(self, pet_health) -> Dict[str, Any]:
        return {
            "pet_id": pet_health.pet_id,
            "date": pet_health.date.isoformat() if pet_health.date else None,
            "weight": pet_health.weight,
            "memo": pet_health.memo,
            "shedding_status": pet_health.shedding_status,
            "monthOfWeight": [],
            "yearOfWeight": []
        }

    # _get_monthly_weight_stats 메소드 수정
    def _get_monthly_weight_stats(self, db: Session, pet_id: str, target_date: date) -> List[Dict[str, Any]]:
        """해당 월의 일별 체중 데이터를 가져옵니다. 데이터가 없는 날에는 null 값을 포함합니다."""
        year = target_date.year
        month = target_date.month

        # 해당 월의 일수 구하기
        _, days_in_month = calendar.monthrange(year, month)

        # 해당 월의 데이터 가져오기
        results = db.query(
            PetHealth.date,
            PetHealth.weight
        ).filter(
            PetHealth.pet_id == pet_id,
            extract('year', PetHealth.date) == year,
            extract('month', PetHealth.date) == month,
            PetHealth.weight.isnot(None)  # weight가 None이 아닌 데이터만
        ).all()

        # 결과를 딕셔너리 형태로 변환
        daily_weights = {r.date.day: r.weight for r in results}

        # 응답 형식에 맞게 데이터 구성 - 모든 일자에 대해 데이터 생성
        monthly_stats = []
        for day in range(1, days_in_month + 1):
            weight_value = daily_weights.get(day, None)  # 데이터 없으면 None
            monthly_stats.append({
                "day": str(day),
                "value": weight_value
            })

        return monthly_stats

    # _get_yearly_weight_stats 메소드 수정
    def _get_yearly_weight_stats(self, db: Session, pet_id: str, target_date: date) -> List[Dict[str, Any]]:
        """해당 연도의 월별 평균 체중 데이터를 가져옵니다. 데이터가 없는 월에는 null 값을 포함합니다."""
        year = target_date.year

        # 해당 연도의 월별 평균 체중 데이터 가져오기
        results = db.query(
            extract('month', PetHealth.date).label('month'),
            func.avg(PetHealth.weight).label('avg_weight')
        ).filter(
            PetHealth.pet_id == pet_id,
            extract('year', PetHealth.date) == year,
            PetHealth.weight.isnot(None)  # weight가 None이 아닌 데이터만
        ).group_by(
            extract('month', PetHealth.date)
        ).all()

        # 결과를 딕셔너리 형태로 변환
        monthly_avg_weights = {int(r.month): r.avg_weight for r in results}

        # 응답 형식에 맞게 데이터 구성 - 모든 월에 대해 데이터 생성
        yearly_stats = []
        for month in range(1, 13):
            weight_value = monthly_avg_weights.get(month, None)  # 데이터 없으면 None
            yearly_stats.append({
                "month": str(month),
                "value": weight_value
            })

        return yearly_stats