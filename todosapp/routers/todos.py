from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from starlette import status
from sqlalchemy.orm import Session
from models import Todos
from database import  SessionLocal

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
    completed: bool


@router.get("/")
def read_all(db: Session = Depends(get_db)):
    """
    Retrieve all todos from the database.

    Parameters:
    - db: The database session.

    Returns:
    - A list of all todos.
    """
    todos = db.query(Todos).all()
    return todos

@router.get("/{id}",status_code = status.HTTP_200_OK)
def get_byid(id: int = Path(ge=0,le=1000) ,db : Session = Depends(get_db)): 
    todos = db.query(Todos).filter(Todos.id == id).first()
    if todos is not None:
        return todos
    raise HTTPException(status_code=404, detail="Todo not found")

@router.post("/todo",status_code = status.HTTP_201_CREATED)
def create_todo(todo: TodoRequest, db: Session = Depends(get_db)):
    new_todo = Todos(title=todo.title, description=todo.description, priority=todo.priority, completed=todo.completed)   
    db.add(new_todo)    
    db.commit()
    
@router.put("/todo/{todo_id}",status_code = status.HTTP_200_OK)
def update_todo(todo_request : TodoRequest , todo_id: int = Path(gt=0), db: Session = Depends(get_db)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.completed = todo_request.completed
    db.commit()
    
@router.delete("/todo/{todo_id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_todo( todo_id: int = Path(gt=0), db: Session = Depends(get_db)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo_model)
    db.commit()