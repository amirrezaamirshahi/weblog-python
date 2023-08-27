# Tty Cacth
# try:
#     users = user_serializer(UserDB.find())
#     return users
# except Exception as ex:
#     raise ex


from bson import ObjectId
from fastapi import FastAPI, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from pymongo import MongoClient
from starlette import status
from bson import json_util
import json
from pymongo import ReturnDocument
from auth.jwtHandler import singJWT
from auth.jwtBearer import jwtBearer

from models.user import UserLoginRequest, UserRequest
from models.post import PostSchema


POST = []
app = FastAPI()

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
    }


def user_serializer(users) -> list:
    return [user_helper(user)for user in users]


def post_helper(post) -> dict:
    return {
        "id": str(post["_id"]),
        "title": post["title"],
        "content": post["content"]
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
@app.post("/login", tags=["user"], status_code=status.HTTP_201_CREATED)
async def handel_login(User: UserLoginRequest):
    user = jsonable_encoder(User)
    findUser = UserDB.find_one({"email": user["email"]})
    if not findUser:
        raise HTTPException(
            status_code=404, detail="User is not registered with this email")

    if findUser["password"] == user["password"]:
        return singJWT(findUser["email"])
    else:
        return "pass not mach"


# 3 Add Post
@app.post("/posts", dependencies=[Depends(jwtBearer())], tags=["post"], status_code=status.HTTP_201_CREATED)
async def create_post(post: PostSchema):
    newPost = jsonable_encoder(post)
    return await add_post(newPost)


# 4 Get All Post
@app.get("/get-all-post", tags=["post"], status_code=status.HTTP_200_OK)
async def get_all_post():
    if PostDB.count_documents({}) == 0:
        raise HTTPException(status_code=404, detail="No Post In DB")

    posts = post_serializer(PostDB.find())
    return posts


# 5 Get All User
@app.get("/get-all-user", tags=["user"], status_code=status.HTTP_200_OK)
async def get_all_user():
    if UserDB.count_documents({}) == 0:
        raise HTTPException(status_code=404, detail="No Post In DB")
    users = user_serializer(UserDB.find())
    return users


# 6 Get User By Id
@app.get("/get-post-by-id/{id}", tags=["post"], status_code=status.HTTP_200_OK)
async def get_post_by_id(id: str):
    post = PostDB.find_one({"_id": ObjectId(id)})
    response = json.loads(json_util.dumps(post))
    return response


#! Complete This Error Handelr
# 7 Upadate Post
@app.put("/posts/update_post/{id}", dependencies=[Depends(jwtBearer())], tags=["post"], status_code=status.HTTP_200_OK)
async def update_post(id: str, post: PostSchema):
    if PostDB.find_one({"_id": ObjectId(id)}):
        post = PostDB.find_one_and_update({"_id": ObjectId(id)}, {
            "$set": dict(post)
        })
    else:
        raise HTTPException(status_code=404, detail="not found")


#! Complete This Error Handelr
# 8 Delete Post
@app.delete("/posts/delete_post/{id}", dependencies=[Depends(jwtBearer())], tags=["post"], status_code=status.HTTP_200_OK)
async def delete_post(id: str):
    PostDB.find_one_and_delete({"_id": ObjectId(id)})
