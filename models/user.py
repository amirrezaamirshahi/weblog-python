from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRequest(BaseModel):
    fullname: str = Field(min_length=3, default=None)
    email: str
    password: str = Field(min_length=3)
    confirmPassword: str

    class Config:
        json_schema_extra = {
            "example": {
                "fullname": "Amir Amirshahi",
                "email": "jdoe@x.edu.ng",
                "password": "amir123",
                "confirmPassword": "amir123"
            }
        }


class UserLoginRequest(BaseModel):
    # email: EmailStr = Field(default=None)
    email: str
    password: str = Field(min_length=3, default=None)
