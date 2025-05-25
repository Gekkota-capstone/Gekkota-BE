# /repository/entity/pet_health_entity.py

from sqlalchemy import Column, String, Date, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from db.database import Base


class PetHealth(Base):
    __tablename__ = "pet_health"
    __table_args__ = {"schema": "capstone"}

    # Composite primary key
    firebase_uid = Column(String, ForeignKey("capstone.user.firebase_uid"), primary_key=True)
    pet_id = Column(String, ForeignKey("capstone.pet.pet_id"), primary_key=True)
    date = Column(Date, primary_key=True)

    weight = Column(Float, nullable=True)
    memo = Column(Text, nullable=True)
    shedding_status = Column(String, nullable=True)

    # Relationships
    user = relationship("User", back_populates="pet_healths")
    pet = relationship("Pet", back_populates="pet_healths")