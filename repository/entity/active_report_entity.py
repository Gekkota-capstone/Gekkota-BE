# /repository/entity/active_report_entity.py

from sqlalchemy import Column, String, Float
from db.database import Base

class ActiveReport(Base):
    __tablename__ = "active_reports"
    __table_args__ = {"schema": "capstone"}

    SN = Column(String(255), primary_key=True, nullable=False)
    DATE = Column(String(8), primary_key=True, nullable=False)
    TIME = Column(String(9), primary_key=True, nullable=False)
    active = Column(Float, nullable=False)