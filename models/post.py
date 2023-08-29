from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field


class PostSchema(BaseModel):
    title: str = Field(...)
    content: str = Field(...)
    user: Optional[str] = None
    comment: list = []

    class Config:
        json_schema_extra = {
            "example": {
                "title": "some",
                "content": "some"
            }
        }

