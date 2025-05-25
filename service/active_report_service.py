# /service/active_report_service.py

from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from repository.active_report_repository import ActiveReportRepository
import pandas as pd


class ActiveReportService:
    def __init__(self):
        self.repository = ActiveReportRepository()

    def save_activity_data(self, db: Session, activity_df: pd.DataFrame) -> int:
        """활동량 데이터를 저장"""
        if activity_df.empty:
            return 0

        count = 0
        try:
            for _, row in activity_df.iterrows():
                self.repository.save_or_update(
                    db,
                    row["SN"],
                    row["DATE"],
                    row["TIME"],
                    row["active"]
                )
                count += 1

            db.commit()
            return count
        except Exception as e:
            db.rollback()
            raise e

    def get_activity_by_date(self, db: Session, device_sn: str, date_str: str) -> List[Dict[str, Any]]:
        """특정 날짜의 활동량 데이터 조회"""
        records = self.repository.get_by_sn_and_date(db, device_sn, date_str)
        return [self._record_to_dict(record) for record in records]

    def get_recent_activity(self, db: Session, device_sn: str, limit: int = 24) -> List[Dict[str, Any]]:
        """최근 활동량 데이터 조회"""
        records = self.repository.get_latest_by_sn(db, device_sn, limit)
        return [self._record_to_dict(record) for record in records]

    def _record_to_dict(self, record) -> Dict[str, Any]:
        """ActiveReport 객체를 딕셔너리로 변환"""
        return {
            "SN": record.SN,
            "DATE": record.DATE,
            "TIME": record.TIME,
            "active": record.active
        }