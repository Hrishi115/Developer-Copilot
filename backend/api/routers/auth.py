from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from sqlalchemy.orm import Session
from typing import Annotated
from jose import jwt
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field, field_validator
from database.database import SessionLocal
from ..schemas.schemas import User as users
from passlib.context import CryptContext
import os
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dotenv import load_dotenv
load_dotenv()


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class UserRequestModel(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    full_name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=100)
    password: str = Field(min_length=2, max_length=10)
    role: str = Field(min_length=2, max_length=20)

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        allowed_roles = {"user", "admin"}
        if v not in allowed_roles:
            raise ValueError("Invalid role")
        return v

class Token(BaseModel):
    access_token: str
    token_type: str

def get_user_from_token(token: str):
    to_decode = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return to_decode

def create_access_token(data: dict):
    encoding_data = data.copy()
    expiry = datetime.now(timezone.utc) + timedelta(minutes=30)
    encoding_data.update({"exp": expiry})
    return jwt.encode(encoding_data, SECRET_KEY, algorithm=ALGORITHM)

def get_currentuser(token: Annotated[str, Depends(oauth2_scheme)]):
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return payload
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or Expired token")
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependancy = Annotated[Session, Depends(get_db)]



@router.post("/", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRequestModel, db: db_dependancy):
    existing_user = db.query(users).filter(users.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    user_to_register = users(
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        hashed_password=bcrypt_context.hash(user.password),
        role=user.role,
        is_active=True
    )

    db.add(user_to_register)
    db.commit()

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependancy):
    user = db.query(users).filter(users.username == form_data.username).first()
    if user is None: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Username")
    if not bcrypt_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Password")
    
    token_data = {
        "sub": user.username,
        "id": user.id,
        "role": user.role
    }

    access_token = create_access_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user(user: Annotated[dict, Depends(get_currentuser)], db: db_dependancy):
    if user is None:
        # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
        return None
    return db.query(users).filter(users.id == user.get("id")).first()