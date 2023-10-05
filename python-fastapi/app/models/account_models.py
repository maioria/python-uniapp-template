from enum import Enum
from typing import List, Dict

from pydantic import BaseModel, constr


class WechatLoginDTO(BaseModel):
    code: str = None
    state: str = None


class VisitorLoginDTO(BaseModel):
    fingerprint: constr(min_length=15)
    

class FeedbackDTO(BaseModel):
    content: constr(min_length=1)
    contact: str = None
