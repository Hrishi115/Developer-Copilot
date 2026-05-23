from fastapi import APIRouter
from services import retrieval

router = APIRouter(
    prefix="/retrieval",
    tags=["retrieval"]
)

@router.get("/{query}")
def query_retrieval(query: str, repo: str):
    """Endpoint to trigger the retrieval pipeline for a given query and repository."""
    try:
        response = retrieval.retrieval_pipeline(query, repo)
    except Exception as e:
        return {"error": str(e)}
    return {"response": response.content}