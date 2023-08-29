from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId
from fastapi import APIRouter,  HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from pymongo import MongoClient
from starlette import status
from bson import json_util
import json

from auth.jwtHandler import singJWT, decodeJWTuser
from auth.jwtBearer import jwtBearer

from models.user import UserLoginRequest, UserRequest, UserCompliteProfile


router = APIRouter()

# Connected DB
client = MongoClient("mongodb://localhost:27017/")
db = client["My-Weblog"]
UserDB = db['User']
PostDB = db['Post']


def user_helper(useruniq) -> dict:
    return {
        "id": str(useruniq["_id"]),
        "fullname": useruniq["fullname"],
        "email": useruniq["email"],
        "password": useruniq["password"],
        "confirmPassword": useruniq["confirmPassword"],
        "tags": useruniq["tags"]
    }


def user_serializer(users) -> list:
    return [user_helper(user)for user in users]


async def add_user(useruniq_data: dict) -> dict:
    useruniq = UserDB.insert_one(useruniq_data)
    new_useruniq = UserDB.find_one({"_id": useruniq.inserted_id})
    return user_helper(new_useruniq)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# 1 Create User
@router.post("/register", tags=["user"], status_code=status.HTTP_201_CREATED)
async def create_user(user: UserRequest):
    newUser = jsonable_encoder(user)

    findEmail = UserDB.find_one({"email": newUser["email"]})
    if not findEmail:
        if newUser["password"] == newUser["confirmPassword"]:
            await add_user(newUser)
            return singJWT(user.email)
        else:
            raise HTTPException(
                status_code=422, detail="password and confrimPassword must same")
    else:
        raise HTTPException(
            status_code=422, detail="There is a user with this email")


# 2 Login User
@router.post("/login", tags=["user"], status_code=status.HTTP_200_OK)
async def handel_login(User: UserLoginRequest):
    user = jsonable_encoder(User)
    findUser = UserDB.find_one({"email": user["email"]})
    if not findUser:
        raise HTTPException(
            status_code=404, detail="User is not registered with this email")

    print(findUser.get("_id"))
    if findUser["password"] == user["password"]:
        return singJWT(str(findUser.get("_id")))
    else:
        raise HTTPException(
            status_code=422, detail="password not mach")


# 3 Complate Profile
@router.post("/user/complate_profile/{id}", dependencies=[Depends(jwtBearer())], tags=["user"])
async def complete_profile(id: str, profile: UserCompliteProfile, token: Annotated[str, Depends(oauth2_scheme)]):
    userID = decodeJWTuser(token)['userID']
    if userID == id:
        myquery = {"_id":  ObjectId(id)}
        newvalues = {"$set": {"age": profile.age, "about": profile.about,
                              "WorkExperience": profile.WorkExperience, "educationalBackground": profile.educationalBackground}}
        UserDB.update_one(myquery, newvalues)
    else:
        raise HTTPException(
            status_code=401, detail="you only can complate your profile")


# 4 Tags
@router.get("/user/same_tags", dependencies=[Depends(jwtBearer())], tags=["user"])
async def find_same_tags(token: Annotated[str, Depends(oauth2_scheme)]):
    userID = decodeJWTuser(token)['userID']
    user = UserDB.find_one({"_id": ObjectId(userID)})
    userTage = []
    allUser = []
    IdList = []
    userTage = user['tags']

    findTags = UserDB.find({})
    for doc in findTags:
        allUser.append(doc)

    tmpFlag = False
    for i in range(len(userTage)):
        for j in range(len(allUser)):
            for k in range(len(allUser[j]['tags'])):
                if allUser[j]['tags'][k] == userTage[i]:
                    IdList.append(allUser[j]["_id"])
                    tmpFlag = True
                    break
                if tmpFlag:
                    tmpFlag = False
                    break

    userList = []
    finalList = list(set(IdList))

    for i in range(len(finalList)):
        user = UserDB.find_one({"_id": ObjectId(finalList[i])})
        userList.append(user)

    return json.loads(json_util.dumps(userList))


# 5 Get All User
@router.get("/get-all-user", tags=["user"], status_code=status.HTTP_200_OK)
async def get_all_user():
    if UserDB.count_documents({}) == 0:
        raise HTTPException(status_code=404, detail="No Post In DB")
    users = user_serializer(UserDB.find())
    return users
