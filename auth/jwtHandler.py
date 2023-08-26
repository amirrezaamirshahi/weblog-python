# This file is responsible for signing , encoding , decoding and returning JWT.

import time

import jwt
from decouple import config

JWT_SECRET = config("SECRET")
JWT_ALGORITGM = config("ALGORITGM")

# Function returns the generated Tokens (JWT)


def token_response(token: str):
    return {
        "sccess token": token
    }


# Function used for signing the JWT string
def singJWT(userID: str):
    payload = {
        "userID": userID,
        "expriy": time.time()+600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITGM)
    return (token_response(token))


def decodeJWT(token: str):
    try:
        decode_token = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITGM)
        return decode_token if decode_token['expires'] >= time.time() else None
    except:
        return {}
