from pydantic import BaseModel, Field


class PostSchema(BaseModel):
    title: str = Field(...)
    content: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "some",
                "content": "some"
            }
        }