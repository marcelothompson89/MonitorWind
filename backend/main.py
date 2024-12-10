from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from backend.app.database import SessionLocal, engine, Base
from backend.app.models import models
from backend.app.api import items, scraping, users
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MonitorWind API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get the absolute path to the static directory
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# Include routers
app.include_router(items.router, prefix="/api", tags=["items"])
app.include_router(scraping.router, prefix="/api", tags=["scraping"])
app.include_router(users.router, prefix="/api/users", tags=["users"])

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Serve index.html for the frontend
@app.get("/")
async def serve_spa(request: Request):
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

# Catch all routes to handle client-side routing
@app.get("/{full_path:path}")
async def serve_spa_paths(full_path: str):
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))
