from fastapi import APIRouter
from services import retrieval
from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str
    repo: str

router = APIRouter(
    prefix="/retrieval",
    tags=["retrieval"]
)

@router.post("/")
def query_retrieval(request: QueryRequest):
    """Endpoint to trigger the retrieval pipeline for a given query and repository."""
    try:
        response = retrieval.retrieval_pipeline(request.query, request.repo)
    except Exception as e:
        return {"error": str(e)}
    return {"response": response.content}