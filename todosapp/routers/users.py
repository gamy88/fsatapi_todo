from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from starlette import status
from sqlalchemy.orm import Session
from models import Todos, Users
from database import  SessionLocal
from.auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(
    prefix="/user",
    tags=["user"]
    
    
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Userverify(BaseModel):
    password: str
    new_password: str = Field(min_length = 5)


@router.get("/todo",status_code = status.HTTP_200_OK)
def get_user(user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    todos = db.query(Todos).filter(Todos.owner_id == user['user_id']).all()
    return todos

@router.put("/password", status_code=status.HTTP_200_OK)
def change_password(user_verify: Userverify, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    user_model = db.query(Users).filter(Users.id == user['user_id']).first()
    
    if not bcrypt.verify(user_verify.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Password incorrect")
    
    user_model.hashed_password = bcrypt.hash(user_verify.new_password)
    db.commit()
    return {"message": "Password changed successfully"}