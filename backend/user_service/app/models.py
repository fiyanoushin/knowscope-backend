
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=True)  # OAuth-safe

    role = Column(String, default="student")

    education = Column(String, nullable=True)
    institution = Column(String, nullable=True)
    year_of_study = Column(String, nullable=True)

    is_active = Column(Boolean, default=True)
