from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

from database import SessionLocal

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
    
)

SECRET_KEY = "helloworld"
ALGORITHM = "HS256"

bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    
class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate_user(username: str, password: str, db: Session):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = { "sub": username, "user_id": user_id }
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_bearer), db: Session = Depends(get_db)):
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
        return{'username': username, 'user_id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(create_user_request: CreateUserRequest, db: Session = Depends(get_db)):
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=bcrypt.hash(create_user_request.password),
        is_active=True,
    )
    db.add(create_user_model)
    db.commit()
    return create_user_model


@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                           db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user: 
        return "Failed Authentication"
    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    
    return {"access_token": token, "token_type": "bearer"}
