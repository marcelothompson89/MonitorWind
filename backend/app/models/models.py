from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

# SQLAlchemy Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relación con las palabras clave
    keywords = relationship("Keyword", back_populates="user")
    
class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relación con el usuario
    user = relationship("User", back_populates="keywords")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    country = Column(String, index=True)
    source_url = Column(String)
    source_type = Column(String, index=True)
    presentation_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    extra_data = Column(Text)  # JSON con información adicional específica de cada fuente

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "country": self.country,
            "url": self.source_url,  # Mapear source_url a url para el frontend
            "date": self.presentation_date,  # Mapear presentation_date a date para el frontend
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "extra_data": self.extra_data
        }

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    url = Column(String, unique=True)
    scraper_type = Column(String)  # Tipo de scraper a usar (ispch, etc.)
    active = Column(Boolean, default=True)  # Activo o inactivo
    created_at = Column(DateTime, default=datetime.utcnow)
    last_scraped = Column(DateTime)
