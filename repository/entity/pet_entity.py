# /repository/entity/pet_entity.py

from sqlalchemy import Column, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base


class Pet(Base):
    __tablename__ = "pet"
    __table_args__ = {"schema": "capstone"}

    pet_id = Column(String, primary_key=True, index=True)
    firebase_uid = Column(String, ForeignKey("capstone.user.firebase_uid"), nullable=False)
    name = Column(String, nullable=False)
    gender = Column(String, nullable=False)  # This will store any gender string value the user inputs
    birthdate = Column(Date, nullable=True)
    species = Column(String, nullable=False)

    # Relationships
    user = relationship("User", back_populates="pets")
    pet_cleans = relationship("PetClean", back_populates="pet", cascade="all, delete-orphan")
    pet_feeds = relationship("PetFeed", back_populates="pet", cascade="all, delete-orphan")
    pet_healths = relationship("PetHealth", back_populates="pet", cascade="all, delete-orphan")
    pet_actives = relationship("PetActive", back_populates="pet", cascade="all, delete-orphan")