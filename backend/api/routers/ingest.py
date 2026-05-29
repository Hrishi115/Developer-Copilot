from fastapi import APIRouter, Depends, HTTPException
from services import ingestion
from typing import Annotated
from api.routers import auth


router = APIRouter(prefix="/ingest", tags=["ingest"])

user_dependancy = Annotated[dict, Depends(auth.get_currentuser)]

@router.post("/{url:path}")
async def ingest_repository(url: str, current_user: user_dependancy):
    """Endpoint to trigger the ingestion pipeline for a given Github repository URL."""
    
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    try: 
        message = ingestion.ingest_pipeline(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": message}