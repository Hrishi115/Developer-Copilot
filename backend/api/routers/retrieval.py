from fastapi import APIRouter, Depends, HTTPException
from services import retrieval
from pydantic import BaseModel
from typing import Annotated
from api.routers import auth

class QueryRequest(BaseModel):
    query: str
    repo: str

router = APIRouter(
    prefix="/retrieval",
    tags=["retrieval"]
)

user_dependancy = Annotated[dict, Depends(auth.get_currentuser)]

@router.post("/")
async def query_retrieval(request: QueryRequest, current_user: user_dependancy):
    """Endpoint to trigger the retrieval pipeline for a given query and repository."""
    if current_user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    try:
        response = retrieval.retrieval_pipeline(request.query, request.repo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"response": response}