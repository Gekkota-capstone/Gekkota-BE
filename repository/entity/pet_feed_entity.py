# /repository/entity/pet_feed_entity.py

from sqlalchemy import Column, String, Date, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from db.database import Base


class PetFeed(Base):
    __tablename__ = "pet_feed"
    __table_args__ = {"schema": "capstone"}

    # Composite primary key
    firebase_uid = Column(String, ForeignKey("capstone.user.firebase_uid"), primary_key=True)
    pet_id = Column(String, ForeignKey("capstone.pet.pet_id"), primary_key=True)
    date = Column(Date, primary_key=True)
    food_type = Column(String, primary_key=True)  # Primary Key에 추가

    food_size = Column(String, nullable=True)
    food_amount = Column(Float, nullable=True)
    amount_unit = Column(String, nullable=True)
    memo = Column(Text, nullable=True)  # message -> memo 변경

    # Relationships
    user = relationship("User", back_populates="pet_feeds")
    pet = relationship("Pet", back_populates="pet_feeds")