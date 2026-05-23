from fastapi import APIRouter
from services import ingestion 

router = APIRouter(prefix="/ingest", tags=["ingest"])

@router.post("/{url:path}")
def ingest_repository(url: str):
    """Endpoint to trigger the ingestion pipeline for a given Github repository URL."""
    try: 
        chroma_db = ingestion.ingest_pipeline(url)
    except Exception as e:
        return {"error": str(e)}
    return {"message": f"Ingestion completed for {url}. Vector Collection created successfully."}