from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from backend.app.database import SessionLocal, engine, Base
from backend.app.models import models
from backend.app.api import items, scraping, users
from fastapi.responses import JSONResponse

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

# Include routers
app.include_router(items.router, prefix="/api", tags=["items"])
app.include_router(scraping.router, prefix="/api/scraping", tags=["scraping"])
app.include_router(users.router, prefix="/api/users", tags=["users"])

@app.get("/")
def root():
    return {"message": "MonitorWind API is running"}
