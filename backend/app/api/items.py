from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..database import SessionLocal
from ..models import models
from sqlalchemy import or_

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/items")
async def get_items(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    country: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user_id: Optional[int] = None,
    use_keywords: bool = False
):
    print(f"Received request - country: '{country}', search: '{search}', user_id: '{user_id}'")
    
    # Start with a base query
    query = db.query(models.Item)
    
    # Si se especifica user_id y use_keywords es True, filtrar por palabras clave del usuario
    if user_id and use_keywords:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Obtener las palabras clave del usuario
        user_keywords = db.query(models.Keyword).filter(models.Keyword.user_id == user_id).all()
        if user_keywords:
            # Crear una condición OR para cada palabra clave
            keyword_conditions = []
            for keyword in user_keywords:
                keyword_conditions.append(
                    or_(
                        models.Item.title.ilike(f"%{keyword.word}%"),
                        models.Item.description.ilike(f"%{keyword.word}%")
                    )
                )
            # Aplicar el filtro de palabras clave
            if keyword_conditions:
                query = query.filter(or_(*keyword_conditions))
    
    if search:
        query = query.filter(
            or_(
                models.Item.title.ilike(f"%{search}%"),
                models.Item.description.ilike(f"%{search}%")
            )
        )
    
    # Apply country filter if provided
    if country:
        print(f"Applying country filter for: '{country}'")
        query = query.filter(models.Item.country.ilike(country))
    
    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        query = query.filter(models.Item.presentation_date >= start_date)
    
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        query = query.filter(models.Item.presentation_date <= end_date)
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination and get items
    items = query.order_by(models.Item.presentation_date.desc()).offset(skip).limit(limit).all()
    
    # Convert items to dictionaries
    items_list = []
    for item in items:
        item_dict = item.to_dict()
        items_list.append(item_dict)
        print(f"Item: {item.title}")
    
    return {
        "total": total,
        "items": items_list
    }

@router.get("/items/{item_id}")
async def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item.to_dict()
