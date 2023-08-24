from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from pymongo import MongoClient
from starlette import status


app = FastAPI()


client = MongoClient("mongodb://localhost:27017/")
db = client["My-Weblog"]
mycol = db['User']


class UserRequest(BaseModel):
    fullname: str = Field(min_length=3)
    email: str
    password: str = Field(min_length=3)
    confirmPassword: str


@app.post("/user/login", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserRequest):
    newUser = jsonable_encoder(user)

    findEmail = mycol.find_one({"email": newUser["email"]})
    if not findEmail:
        if newUser["password"] == newUser["confirmPassword"]:
            return mycol.insert_one(newUser)
        else:
            raise HTTPException(
                status_code=422, detail="password and confrimPassword must same")
    else:
        raise HTTPException(
            status_code=422, detail="There is a user with this email")
