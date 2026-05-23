from fastapi import FastAPI
from .routers import ingest, retrieval
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(ingest.router)
app.include_router(retrieval.router)

@app.get("/")
async def health_check():
    return {"status": "ok"}
