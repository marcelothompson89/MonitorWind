from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import SessionLocal
from ..models import models
from pydantic import BaseModel
from datetime import datetime
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquemas Pydantic para validación
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

class KeywordBase(BaseModel):
    word: str

class KeywordCreate(KeywordBase):
    pass

class Keyword(KeywordBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/", response_model=User)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Verificar si el usuario ya existe
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/{user_id}/keywords/", response_model=Keyword)
async def create_keyword(
    user_id: int,
    keyword: KeywordCreate,
    db: Session = Depends(get_db)
):
    # Verificar si el usuario existe
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Crear nueva palabra clave
    db_keyword = models.Keyword(word=keyword.word, user_id=user_id)
    db.add(db_keyword)
    db.commit()
    db.refresh(db_keyword)
    return db_keyword

@router.get("/{user_id}/keywords/", response_model=List[Keyword])
async def get_user_keywords(user_id: int, db: Session = Depends(get_db)):
    # Verificar si el usuario existe
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return db.query(models.Keyword).filter(models.Keyword.user_id == user_id).all()

@router.delete("/{user_id}/keywords/{keyword_word}")
async def delete_keyword(
    user_id: int,
    keyword_word: str,
    db: Session = Depends(get_db)
):
    # Verificar si la palabra clave existe y pertenece al usuario
    keyword = db.query(models.Keyword).filter(
        models.Keyword.word == keyword_word,
        models.Keyword.user_id == user_id
    ).first()
    
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")
    
    db.delete(keyword)
    db.commit()
    return {"message": "Keyword deleted successfully"}
