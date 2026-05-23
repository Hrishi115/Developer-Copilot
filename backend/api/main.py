from fastapi import FastAPI
from .routers import ingest, retrieval
app = FastAPI()

app.include_router(ingest.router)
app.include_router(retrieval.router)

@app.get("/")
async def health_check():
    return {"status": "ok"}
