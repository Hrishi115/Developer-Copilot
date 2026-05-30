# from datetime import datetime, timedelta, timezone
# from fastapi import Depends, HTTPException
# from typing import Annotated
# from database.database import SessionLocal
# from .routers import auth
# from .schemas.schemas import User as users

# DAILY_QUERY_LIMIT = 10  # tune this

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# db_dependancy = Annotated[dict, Depends(get_db)]
# user_dependancy = Annotated[dict, Depends(auth.get_currentuser)]    

# def check_query_limit(current_user: user_dependancy, db: db_dependancy, type: str):
#     user = db.query(users).filter(users.id == current_user["id"]).first()
    
#     if 