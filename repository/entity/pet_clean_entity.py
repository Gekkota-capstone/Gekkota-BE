# /repository/entity/pet_clean_entity.py

from sqlalchemy import Column, String, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from db.database import Base


class PetClean(Base):
    __tablename__ = "pet_clean"
    __table_args__ = {"schema": "capstone"}

    # Composite primary key
    firebase_uid = Column(String, ForeignKey("capstone.user.firebase_uid"), primary_key=True)
    pet_id = Column(String, ForeignKey("capstone.pet.pet_id"), primary_key=True)
    date = Column(Date, primary_key=True)

    memo = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="pet_cleans")
    pet = relationship("Pet", back_populates="pet_cleans")