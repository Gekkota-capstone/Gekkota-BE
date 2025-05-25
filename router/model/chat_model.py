# /router/model/chat_model.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatMessage(BaseModel):
    id: int
    question: str
    answer: Optional[str] = None
    created_at: datetime


class ChatQuery(BaseModel):
    question: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    messages: List[ChatMessage]

    class Config:
        from_attributes = True