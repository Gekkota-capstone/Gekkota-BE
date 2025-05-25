# /router/model/rtsp_model.py

from pydantic import BaseModel
from typing import List


class RtspResponse(BaseModel):
    rtsp_url: str

    class Config:
        from_attributes = True