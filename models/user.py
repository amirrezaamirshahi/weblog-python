from ast import List
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRequest(BaseModel):
    fullname: str = Field(min_length=3, default=None)
    email: str
    password: str = Field(min_length=3)
    confirmPassword: str
    tags: list = []
    age: Optional[str] = None
    about: Optional[str] = None
    WorkExperience: Optional[str] = None
    educationalBackground: Optional[str] = None

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


class UserCompliteProfile(BaseModel):
    age : Optional[str] = None
    about : Optional[str] = None
    WorkExperience : Optional[str] = None
    educationalBackground : Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "age": "18",
                "about": "i like sport",
                "WorkExperience": "2 year in tehran",
                "educationalBackground": "kashan uni"
            }
        }
