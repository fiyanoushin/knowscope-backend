from fastapi import FastAPI
from .routes import router
from .database import engine
from .models import Base

app = FastAPI()  

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "User service running"}

