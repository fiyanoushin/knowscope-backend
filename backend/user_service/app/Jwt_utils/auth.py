from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPBearer
from jose import jwt
# from app.database import blacklist_collection
import os
from datetime import datetime, timedelta

security = HTTPBearer()
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # token endpoint

def get_current_user(token: str = Depends(oauth2_scheme)):
    # blacklisted =await blacklist_collection.find_one({"token": token})
    # if blacklisted:
    #     raise HTTPException(status_code=401, detail="Token has been revoked")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user_id}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")



def get_current_admin(token=Depends(security)):
    payload = get_current_user(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized as admin")
    return payload