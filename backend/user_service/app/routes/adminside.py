from typing import Optional
from fastapi import APIRouter, UploadFile, Form, Depends ,Depends, HTTPException, Header
from app.database import student_collection
from app.utils import save_image
# from app.Jwt_utils.auth import get_current_user
from .jwt_handler import get_current_user
from bson import ObjectId



async def get_user_from_header(authorization: str = Header(...)):
            
    print("Authorization header received:", authorization)
    token = authorization.split(" ")[1] 
    try:
        return get_current_user(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    
    