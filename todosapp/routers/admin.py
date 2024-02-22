from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from starlette import status
from sqlalchemy.orm import Session
from models import Todos
from database import  SessionLocal
from.auth import get_current_user

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
    
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/todo",status_code = status.HTTP_200_OK)
def read_all(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    todos = db.query(Todos).all()
    return todos 

@router.delete("/todo/(todo_id)", status_code=status.HTTP_204_NO_CONTENT)
def delete_by_id(todo_id: int, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()

