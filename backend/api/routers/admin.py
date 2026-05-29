from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from typing import Annotated
from database.database import SessionLocal
from ..routers import auth
from sqlalchemy.orm import Session
from ..schemas import schemas as models

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

db_dependancy = Annotated[Session, Depends(get_db)]

@router.get("/get_all_users")
async def get_all_users(current_user: Annotated[dict, Depends(auth.get_currentuser)], db: Annotated[Session, Depends(get_db)]):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access Forbidden")
    
    return db.query(models.User).all()