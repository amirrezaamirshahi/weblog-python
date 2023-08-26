
# from pymongo import MongoClient


# def connectedDB():
#     client = MongoClient("mongodb://localhost:27017/")
#     db = client["My-Weblog"]
#     mycol = db['User']
#     print("Connect to db")


# def user_helper(useruniq) -> dict:
#     return {
#         "id": str(useruniq["_id"]),
#         "fullname": useruniq["fullname"],
#         "email": useruniq["email"],
#         "password": useruniq["password"],
#         "confirmPassword": useruniq["confirmPassword"],
#     }


# async def add_user(useruniq_data: dict) -> dict:
#     useruniq = mycol.insert_one(useruniq_data)
#     new_useruniq = mycol.find_one({"_id": useruniq.inserted_id})
#     return user_helper(new_useruniq)
