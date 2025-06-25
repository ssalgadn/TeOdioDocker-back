from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Union
from app.models.models import GameEnum, ProductTypeEnum


class CommentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user: str
    product_id: int
    text: str
    date: datetime

class CommentCreate(BaseModel):
    user: str
    product_id: int
    text: str

class CommentResponse(CommentBase):
    pass
