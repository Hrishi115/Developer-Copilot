from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from database.database import SessionLocal
from services import ingestion
from typing import Annotated
from api.routers import auth
# from api.dependancies import check_query_limit
from ..schemas.schemas import User as users

router = APIRouter(prefix="/ingest", tags=["ingest"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependancy = Annotated[dict, Depends(get_db)]
user_dependancy = Annotated[dict, Depends(auth.get_currentuser)]

MAX_INGESTS_PER_DAY = 5

# def check_ingest_limit(current_user: user_dependancy, db: db_dependancy):
#     user = db.query(users).filter(users.id == current_user["id"]).first()
    
#     # Reset counter daily
#     if datetime.now(timezone.utc) - user.ingest_reset_at > timedelta(days=1):
#         user.ingest_count = 0
#         user.ingest_reset_at = datetime.now(timezone.utc)
    
#     if user.ingest_count >= MAX_INGESTS_PER_DAY:
#         raise HTTPException(status_code=429, detail="Daily ingest limit reached")
    
#     user.ingest_count += 1
#     db.commit()

@router.post("/{url:path}")
async def ingest_repository(url: str, current_user: user_dependancy, db: db_dependancy):
    """Endpoint to trigger the ingestion pipeline for a given Github repository URL."""
    
    user = db.query(users).filter(users.id == current_user["id"]).first()

    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    if user.ingest_query_count >= MAX_INGESTS_PER_DAY:
        raise HTTPException(status_code=429, detail="Daily ingestion query limit reached")

    try: 
        message = ingestion.ingest_pipeline(url, user_id=current_user["id"])
        if not message["ingestion_skipped"]:    
            db.query(users).filter(users.id == current_user["id"]).update({"ingest_query_count": user.ingest_query_count + 1})
            db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": message}