# /repository/entity/pet_active_entity.py

from sqlalchemy import Column, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from db.database import Base


class PetActive(Base):
    __tablename__ = "pet_active"
    __table_args__ = {"schema": "capstone"}

    # Composite primary key
    firebase_uid = Column(String, ForeignKey("capstone.user.firebase_uid"), primary_key=True)
    pet_id = Column(String, ForeignKey("capstone.pet.pet_id"), primary_key=True)

    abnormalBehavior = Column(String, nullable=True)
    highlightVideoUrl = Column(String, nullable=True)
    bioPattern = Column(Text, nullable=True)
    heatmapImageUrl = Column(String, nullable=True)
    timeOfActivity = Column(String, nullable=True)
    recentDatOfActivity = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="pet_actives")
    pet = relationship("Pet", back_populates="pet_actives")