# /repository/entity/user_entity.py

from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from db.database import Base


class User(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": "capstone"}

    firebase_uid = Column(String, primary_key=True, index=True)
    nickname = Column(String, nullable=False)
    profile = Column(Text, nullable=True)

    # Relationships
    pets = relationship("Pet", back_populates="user", cascade="all, delete-orphan")
    pet_cleans = relationship("PetClean", back_populates="user", cascade="all, delete-orphan")
    pet_feeds = relationship("PetFeed", back_populates="user", cascade="all, delete-orphan")
    pet_healths = relationship("PetHealth", back_populates="user", cascade="all, delete-orphan")
    pet_actives = relationship("PetActive", back_populates="user", cascade="all, delete-orphan")
    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")