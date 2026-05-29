from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from api.routers import auth
from sqlalchemy.orm import Session
from database.database import SessionLocal
from api.schemas.schemas import User as users
from starlette import status
from pydantic import BaseModel, Field

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

class UserVerificationModel(BaseModel):
    password: str = Field(min_length=2, max_length=10)
    new_password: str = Field(min_length=2, max_length=10)

user_dependancy = Annotated[dict, Depends(auth.get_currentuser)]  
db_dependancy = Annotated[Session, Depends(get_db)]

@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user(user: Annotated[dict, Depends(auth.get_currentuser)], db: db_dependancy):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    return db.query(users).filter(users.id == user.get("id")).first()

@router.put("/change_password", status_code=status.HTTP_200_OK)
async def change_password(user_verification: UserVerificationModel, user: user_dependancy, db: db_dependancy):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    user_in_db = db.query(users).filter(users.id == user.get("id")).first()

    if not auth.bcrypt_context.verify(user_verification.password, user_in_db.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect Password")
    
    updated_password = auth.bcrypt_context.hash(user_verification.new_password)
    db.query(users).filter(users.id == user.get("id")).update({"hashed_password": updated_password})
    db.commit()
    return {"detail": "Password updated successfully"}