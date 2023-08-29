# Tty Cacth
# try:
#     users = user_serializer(UserDB.find())
#     return users
# except Exception as ex:
#     raise ex

from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from pymongo import MongoClient
from starlette import status
from bson import json_util
import json
import jwt
from pymongo import ReturnDocument
from auth.jwtHandler import singJWT, decodeJWTuser
from auth.jwtBearer import jwtBearer

from models.user import UserLoginRequest, UserRequest, UserCompliteProfile
from models.post import PostSchema


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


POST = []
app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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


def post_helper(post) -> dict:
    return {
        "id": str(post["_id"]),
        "title": post["title"],
        "content": post["content"],
        "user": post["user"]
    }


def post_serializer(posts) -> list:
    return [post_helper(post)for post in posts]


async def add_user(useruniq_data: dict) -> dict:
    useruniq = UserDB.insert_one(useruniq_data)
    new_useruniq = UserDB.find_one({"_id": useruniq.inserted_id})
    return user_helper(new_useruniq)


async def add_post(post_data: dict) -> dict:
    post = PostDB.insert_one(post_data)
    new_post = PostDB.find_one({"_id": post.inserted_id})
    return post_helper(new_post)


# 1 Create User
@app.post("/register", tags=["user"], status_code=status.HTTP_201_CREATED)
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


# 2 Handel Login
@app.post("/login", tags=["user"], status_code=status.HTTP_200_OK)
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
        return "pass not mach"


# Complete Profile
@app.post("/user/complate_profile/{id}", dependencies=[Depends(jwtBearer())], tags=["user"])
async def complete_profile(id: str, profile: UserCompliteProfile, token: Annotated[str, Depends(oauth2_scheme)]):
    userID = decodeJWTuser(token)['userID']
    if userID == id:
        print("OK")
        myquery = {"_id":  ObjectId(id)}
        newvalues = {"$set": {"age": profile.age, "about": profile.about,
                              "WorkExperience": profile.WorkExperience, "educationalBackground": profile.educationalBackground}}
        UserDB.update_one(myquery, newvalues)
    else:
        raise HTTPException(
            status_code=404, detail="you only can update your post")


# Find Same Tags
@app.get("/user/same_tags", dependencies=[Depends(jwtBearer())], tags=["user"])
async def find_same_tags(token: Annotated[str, Depends(oauth2_scheme)]):
    userID = decodeJWTuser(token)['userID']
    user = UserDB.find_one({"_id": ObjectId(userID)})
    print(user)
    userTage = []
    allUser = []
    IdList = []
    userTage = user['tags']
    print("User Tag : ", userTage)

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


# 3 Add Post
@app.post("/posts", dependencies=[Depends(jwtBearer())], tags=["post"], status_code=status.HTTP_201_CREATED)
async def create_post(post: PostSchema, token: Annotated[str, Depends(oauth2_scheme)]):
    post.user = decodeJWTuser(token)['userID']
    newPost = jsonable_encoder(post)
    return await add_post(newPost)


# Updfate Post
@app.put("/posts/update/{id}", tags=["post"], dependencies=[Depends(jwtBearer())], status_code=status.HTTP_200_OK)
async def update(id: str, post: PostSchema, token: Annotated[str, Depends(oauth2_scheme)]):
    userID = decodeJWTuser(token)['userID']
    findPost = PostDB.find_one({"_id": ObjectId(id)})
    print(findPost)

    if userID == findPost['user']:
        myquery = {"_id":  ObjectId(id)}
        newvalues = {"$set": {"title": post.title, "content": post.content}}
        PostDB.update_one(myquery, newvalues)
    else:
        raise HTTPException(
            status_code=404, detail="you only can update your post")


#! Complete This Error Handelr
# 5 Delete Post
@app.delete("/posts/delete_post/{id}", dependencies=[Depends(jwtBearer())], tags=["post"], status_code=status.HTTP_200_OK)
async def delete_post(id: str, token: Annotated[str, Depends(oauth2_scheme)]):
    findPostForDelete = PostDB.find_one({"_id": ObjectId(id)})

    if decodeJWTuser(token)['userID'] == findPostForDelete['user']:
        PostDB.find_one_and_delete({"_id": ObjectId(id)})

        return {"Delete was successful"}
    else:
        raise HTTPException(
            status_code=404, detail="There is no post with this id or you did not register the post")


# 6 Get All Post
@app.get("/get-all-post", tags=["post"], status_code=status.HTTP_200_OK)
async def get_all_post():
    if PostDB.count_documents({}) == 0:
        raise HTTPException(status_code=404, detail="No Post In DB")
    posts = post_serializer(PostDB.find())
    return posts


# 7 Get All User
@app.get("/get-all-user", tags=["user"], status_code=status.HTTP_200_OK)
async def get_all_user():
    if UserDB.count_documents({}) == 0:
        raise HTTPException(status_code=404, detail="No Post In DB")
    users = user_serializer(UserDB.find())
    return users


# 8 Get User By Id
@app.get("/get-post-by-id/{id}", tags=["post"], status_code=status.HTTP_200_OK)
async def get_post_by_id(id: str):
    post = PostDB.find_one({"_id": ObjectId(id)})
    response = json.loads(json_util.dumps(post))
    return response


# # 9 Add Comment
# @app.post("/posts/add-comment/{id}", dependencies=[Depends(jwtBearer())], tags=["post"], status_code=status.HTTP_200_OK)
# async def add_comment(commnet: commentSchema, id: str, token: Annotated[str, Depends(oauth2_scheme)]):
#     findPostForComment = PostDB.find_one({"_id": ObjectId(id)})
#     if findPostForComment:
#         print(commnet)

# # Tag Update
# @app.put("/user/tag_update/{tag}", dependencies=[Depends(jwtBearer())], tags=["user"])
# async def tag_update(tag: str, token: Annotated[str, Depends(oauth2_scheme)]):
#     userID = decodeJWTuser(token)['userID']
#     print(tag)

#     UserDB.update_one({"_id": userID}, {"$set": {"tags": tag}})
#     return "OK"

# # Add Tags
# @app.post("/login", dependencies=[Depends(jwtBearer())], tags=["user"], status_code=status.HTTP_200_OK)
# async def add_tags(tag:UserRequest, token: Annotated[str, Depends(oauth2_scheme)]):
#     userID = decodeJWTuser(token)['userID']
#     findUser =UserDB.find_one({"_id": userID})
#     print(findUser)
