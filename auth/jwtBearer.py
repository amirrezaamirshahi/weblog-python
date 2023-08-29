# The function of this file is to cheack wheather the req is authorized not [verification of the protecd route]
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .jwtHandler import decodeJWT


class jwtBearer(HTTPBearer):
    def __init__(self, auto_Error: bool = True):
        super(jwtBearer, self).__init__(auto_error=auto_Error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(jwtBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid or Expired token")
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=403, detail="Invalid or Expired token")

    def verify_jwt(self, jwtoken: str):
        isTokenValid: bool = False
        payload = decodeJWT(jwtoken)
        if payload:
            isTokenValid = True
        return isTokenValid
