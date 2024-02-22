from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from starlette import status
from sqlalchemy.orm import Session
from models import Todos
from database import  SessionLocal
from.auth import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
class TodoRequest(BaseModel):
    title: str = Field(min_length = 3)
    description: str = Field(max_length = 100)
    priority: int = Field(ge=0, le=6)
    complete: bool


@router.get("/")
def read_all(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    todos = db.query(Todos).filter(Todos.owner_id == user['user_id']).all()
    return todos

@router.get("/todo/{todo_id}",status_code = status.HTTP_200_OK)
def get_by_id(user: str = Depends(get_current_user) ,todo_id: int = Path(ge=0,le=1000) ,db : Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
     
    todos = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user['user_id']).first()
    if todos is not None:
        return todos
    raise HTTPException(status_code=404, detail="Todo not found")

@router.post("/todo", status_code=status.HTTP_201_CREATED)
def create_todo(todo_request: TodoRequest, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None: 
        raise HTTPException(status_code=401, detail="Unauthorized")
    todo_model = Todos(**todo_request.model_dump(), owner_id=user['user_id'])
    db.add(todo_model)
    db.commit()
    
    
    
@router.put("/todo/{todo_id}",status_code = status.HTTP_200_OK)
def update_todo(todo_request : TodoRequest , todo_id: int = Path(gt=0), db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    if user is None: 
        raise HTTPException(status_code=401, detail="Unauthorized")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user['user_id']).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete
    db.commit()
    return "added successfully"
    
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int = Path(..., gt=0), db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user['user_id']).delete()
    db.commit()