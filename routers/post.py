from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId
from fastapi import APIRouter,  HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from pymongo import MongoClient
from starlette import status
from bson import json_util
import json

from auth.jwtHandler import decodeJWTuser
from auth.jwtBearer import jwtBearer

from models.post import PostSchema

router = APIRouter()

# Connected DB
client = MongoClient("mongodb://localhost:27017/")
db = client["My-Weblog"]
UserDB = db['User']
PostDB = db['Post']


def post_serializer(posts) -> list:
    return [post_helper(post)for post in posts]


def post_helper(post) -> dict:
    return {
        "id": str(post["_id"]),
        "title": post["title"],
        "content": post["content"],
        "user": post["user"]
    }


async def add_post(post_data: dict) -> dict:
    post = PostDB.insert_one(post_data)
    new_post = PostDB.find_one({"_id": post.inserted_id})
    return post_helper(new_post)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# 1 Add Post
@router.post("/posts", dependencies=[Depends(jwtBearer())], tags=["post"], status_code=status.HTTP_201_CREATED)
async def create_post(post: PostSchema, token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        post.user = decodeJWTuser(token)['userID']
        newPost = jsonable_encoder(post)
        return await add_post(newPost)
    except Exception as ex:
        raise ex


# 2 Updfate Post
@router.put("/posts/update/{id}", tags=["post"], dependencies=[Depends(jwtBearer())], status_code=status.HTTP_200_OK)
async def update(id: str, post: PostSchema, token: Annotated[str, Depends(oauth2_scheme)]):
    userID = decodeJWTuser(token)['userID']
    findPost = PostDB.find_one({"_id": ObjectId(id)})

    if userID == findPost['user']:
        myquery = {"_id":  ObjectId(id)}
        newvalues = {"$set": {"title": post.title, "content": post.content}}
        PostDB.update_one(myquery, newvalues)
    else:
        raise HTTPException(
            status_code=404, detail="you only can update your post")


# 3 Delete Post
@router.delete("/posts/delete_post/{id}", dependencies=[Depends(jwtBearer())], tags=["post"], status_code=status.HTTP_200_OK)
async def delete_post(id: str, token: Annotated[str, Depends(oauth2_scheme)]):
    findPostForDelete = PostDB.find_one({"_id": ObjectId(id)})

    if decodeJWTuser(token)['userID'] == findPostForDelete['user']:
        PostDB.find_one_and_delete({"_id": ObjectId(id)})

        return {"Delete was successful"}
    else:
        raise HTTPException(
            status_code=404, detail="There is no post with this id or you did not register the post")


# 4 Get All Post
@router.get("/get-all-post", tags=["post"], status_code=status.HTTP_200_OK)
async def get_all_post():
    if PostDB.count_documents({}) == 0:
        raise HTTPException(status_code=404, detail="No Post In DB")
    posts = post_serializer(PostDB.find())
    return posts


# 5 Get post By Id
@router.get("/get-post-by-id/{id}", tags=["post"], status_code=status.HTTP_200_OK)
async def get_post_by_id(id: str):
    post = PostDB.find_one({"_id": ObjectId(id)})
    response = json.loads(json_util.dumps(post))
    return response
