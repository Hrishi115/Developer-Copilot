from fastapi import FastAPI
from .routers import ingest, retrieval
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from database.database import engine
from .routers import admin, auth, user
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from core.logging import get_logger

logger = get_logger()

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    logger.info("Application started")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(ingest.router)
app.include_router(retrieval.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(admin.router)

@app.get("/")
async def health_check():
    return {"status": "ok"}
