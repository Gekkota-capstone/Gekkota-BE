# /repository/entity/chat_entity.py

from sqlalchemy import Column, String, Text, ForeignKey, Integer, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.database import Base


class Chat(Base):
    __tablename__ = "chat"
    __table_args__ = {"schema": "capstone"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    firebase_uid = Column(String, ForeignKey("capstone.user.firebase_uid"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())

    # Relationships
    user = relationship("User", back_populates="chats")