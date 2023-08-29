from typing import Optional
from pydantic import BaseModel, Field


class Comment(BaseModel):
    userForComment: Optional[str] = None
    text: Optional[str] = None


class PostSchema(BaseModel):
    title: str = Field(...)
    content: str = Field(...)
    user: Optional[str] = None
    comment: list = []
    comment: list[Comment] | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "some",
                "content": "some"
            }
        }
