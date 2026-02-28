from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException
from jose import jwt, JWTError, ExpiredSignatureError
import os

security = HTTPBearer()

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM")


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        role = payload.get("role")
        if not user_id or not role:
            raise JWTError("Invalid token payload")
        return {"user_id": user_id,"email": payload.get("email"),"role": role}
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user_from_header(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return decode_access_token(token)


def require_admin(current_user: dict = Depends(get_current_user_from_header)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403,detail="Admin access required")
    return current_user