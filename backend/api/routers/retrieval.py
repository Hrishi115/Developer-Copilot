from fastapi import APIRouter, Depends, HTTPException
from api.schemas.schemas import User as users
from database.database import SessionLocal
from services import retrieval
from pydantic import BaseModel
from typing import Annotated
from api.routers import auth

DAILY_QUERY_LIMIT = 5

class QueryRequest(BaseModel):
    query: str
    repo: str

router = APIRouter(
    prefix="/retrieval",
    tags=["retrieval"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependancy = Annotated[dict, Depends(get_db)]
user_dependancy = Annotated[dict, Depends(auth.get_currentuser)]



# def check_retrieval_limit(current_user: user_dependancy, db: db_dependancy):
#     user = db.query(User).filter(User.id == current_user["id"]).first()
    
#     # Reset counter daily
#     if datetime.now(timezone.utc) - user.retrieval_query_reset_at > timedelta(days=1):
#         user.retrieval_query_count = 0
#         user.retrieval_query_reset_at = datetime.now(timezone.utc)
    
#     if user.retrieval_query_count >= DAILY_QUERY_LIMIT:
#         raise HTTPException(status_code=429, detail="Daily retrieval query limit reached")
    
#     user.retrieval_query_count += 1
#     db.commit()

@router.post("/")
async def query_retrieval(request: QueryRequest, current_user: user_dependancy, db: db_dependancy):
    """Endpoint to trigger the retrieval pipeline for a given query and repository."""
    user = db.query(users).filter(users.id == current_user["id"]).first()

    if current_user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    
    if user.retrieval_query_count >= DAILY_QUERY_LIMIT:
        raise HTTPException(status_code=429, detail="Daily retrieval query limit reached")
    try:
        response = retrieval.retrieval_pipeline(request.query, request.repo, user.id)
        db.query(users).filter(users.id == current_user["id"]).update({"retrieval_query_count": user.retrieval_query_count + 1})
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"response": response}