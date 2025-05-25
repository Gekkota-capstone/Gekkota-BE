# /router/model/pet_state_model.py

from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class KeypointInfo(BaseModel):
    name: str
    conf: float

class HideLog(BaseModel):
    timestamp: str
    reason: str
    low_conf: Optional[List[KeypointInfo]] = None

class PetStateResponse(BaseModel):
    pet_id: str
    is_hiding: bool