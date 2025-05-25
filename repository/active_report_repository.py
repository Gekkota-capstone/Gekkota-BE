# /repository/active_report_repository.py

from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import text
from repository.entity.active_report_entity import ActiveReport


class ActiveReportRepository:
    def save_or_update(self, db: Session, SN: str, DATE: str, TIME: str, active: float) -> bool:
        """활동량 데이터를 저장하거나 업데이트"""
        try:
            # 기존 레코드 확인
            existing = db.query(ActiveReport).filter(
                ActiveReport.SN == SN,
                ActiveReport.DATE == DATE,
                ActiveReport.TIME == TIME
            ).first()

            if existing:
                # 레코드 업데이트
                existing.active = active
            else:
                # 새 레코드 추가
                db_record = ActiveReport(
                    SN=SN,
                    DATE=DATE,
                    TIME=TIME,
                    active=active
                )
                db.add(db_record)

            return True
        except Exception as e:
            raise e

    def get_by_sn_and_date(self, db: Session, SN: str, DATE: str) -> List[ActiveReport]:
        """특정 장치 및 날짜의 모든 활동량 데이터 조회"""
        return db.query(ActiveReport).filter(
            ActiveReport.SN == SN,
            ActiveReport.DATE == DATE
        ).all()

    def get_latest_by_sn(self, db: Session, SN: str, limit: int = 24) -> List[ActiveReport]:
        """특정 장치의 최근 활동량 데이터 조회 (기본 24시간)"""
        query = text(f"""
            SELECT "SN", "DATE", "TIME", active 
            FROM capstone.active_reports 
            WHERE "SN" = :sn
            ORDER BY "DATE" DESC, "TIME" DESC
            LIMIT :limit
        """)

        result = db.execute(query, {"sn": SN, "limit": limit})

        return [ActiveReport(
            SN=row[0],
            DATE=row[1],
            TIME=row[2],
            active=row[3]
        ) for row in result]