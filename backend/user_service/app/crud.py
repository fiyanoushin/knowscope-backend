from sqlalchemy.orm import Session
from .models import User


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_oauth_user(db: Session, email: str, full_name: str):
    user = User(email=email,full_name=full_name,password=None )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
