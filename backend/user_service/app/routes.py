from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .crud import get_user_by_email, create_oauth_user
from .auth_utils import create_access_token
from .google_auth import verify_google_token
from .schemas import GoogleAuthRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/google")
async def google_login(payload: GoogleAuthRequest,db: Session = Depends(get_db)):
    google_user = await verify_google_token(payload.token)

    email = google_user["email"]
    name = google_user.get("name", "")

    user = get_user_by_email(db, email)
    if not user:
        user = create_oauth_user(db, email, name)
    jwt_token = create_access_token({"sub": str(user.id),"email": user.email})
    return {"access_token": jwt_token,"token_type": "bearer"}
