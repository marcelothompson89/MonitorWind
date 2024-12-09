from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from datetime import datetime
from ..database import SessionLocal
from ..models import models
from ..scrapers.anamed_scraper import scrape_anamed
from ..scrapers.congreso_scraper import scrape_congreso
from ..scrapers.expediente_scraper import scrape_expediente
from ..scrapers.digesa_scraper import scrape_digesa
from ..scrapers.digesa_noticias_scraper import scrape_digesa_noticias
from ..scrapers.diputados_noticias_scraper import scrape_diputados_noticias
from ..scrapers.diputados_proyectos_scraper import scrape_diputados_proyectos
from ..scrapers.ispch_noticias_scraper import scrape_ispch_noticias
from ..scrapers.ispch_resoluciones_scraper import scrape_ispch_resoluciones
from ..scrapers.minsa_normas_scraper import scrape_minsa_normas
from ..scrapers.minsa_noticias_scraper import scrape_minsa_noticias
from ..scrapers.senado_noticias_scraper import scrape_senado_noticias
from ..scrapers.digemid_noticias_scraper import scrape_digemid_noticias

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def save_items_to_db(items, source_id: int, db: Session):
    try:
        print(f"Intentando guardar {len(items)} items")
        for item in items:
            try:
                # Verificar si el item ya existe por título y fecha o URL
                existing_item = db.query(models.Item).filter(
                    or_(
                        and_(
                            models.Item.title == item['title'],
                            models.Item.presentation_date == item['presentation_date']
                        ),
                        models.Item.source_url == item['source_url']
                    )
                ).first()
                
                if not existing_item:
                    print(f"Guardando nuevo item: {item['title']} - País: {item['country']}")
                    print(f"Fecha: {item['presentation_date']}")
                    print(f"URL: {item['source_url']}")
                    print(f"Source Type: {item['source_type']}")
                    
                    # Asegurarse de que los campos de texto estén en UTF-8
                    title = item['title'].encode('utf-8').decode('utf-8')
                    description = item['description'].encode('utf-8').decode('utf-8')
                    
                    # Verificar que el source_type existe
                    source = db.query(models.Source).filter(models.Source.scraper_type == item['source_type']).first()
                    if not source:
                        print(f"Error: Source type {item['source_type']} not found")
                        continue
                    
                    db_item = models.Item(
                        title=title,
                        description=description,
                        country=item['country'],
                        source_url=item['source_url'],
                        source_type=item['source_type'],
                        presentation_date=item['presentation_date'],
                        extra_data=item.get('extra_data')
                    )
                    db.add(db_item)
                    db.flush()  # Flush to get the ID
                else:
                    print(f"Item ya existe: {item['title']}")
            except Exception as item_error:
                print(f"Error procesando item individual: {str(item_error)}")
                print(f"Item problemático: {item}")
                continue
        
        db.commit()
        print("Items guardados exitosamente")
    except Exception as e:
        db.rollback()
        print(f"Error detallado al guardar items: {str(e)}")
        print(f"Tipo de error: {type(e)}")
        raise

@router.get("/sources")
async def get_sources(db: Session = Depends(get_db)):
    sources = db.query(models.Source).all()
    return sources

@router.post("/scrape/{source_id}")
async def trigger_scraping(
    source_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    source = db.query(models.Source).filter(models.Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    # Actualizar timestamp de último scraping
    source.last_scraped = datetime.utcnow()
    db.commit()
    
    # Iniciar scraping según el tipo de fuente
    if source.scraper_type == "anamed_cl":
        items = await scrape_anamed()
        if items:
            await save_items_to_db(items, source_id, db)
            return {"message": f"Scraping completado. Se encontraron {len(items)} items."}
        return {"message": "Scraping completado. No se encontraron nuevos items."}
    elif source.scraper_type == "congreso_pe":
        items = await scrape_congreso()
        if items:
            await save_items_to_db(items, source_id, db)
            return {"message": f"Scraping completado. Se encontraron {len(items)} items."}
        return {"message": "Scraping completado. No se encontraron nuevos items."}
    elif source.scraper_type == "expediente_pe":
        items = await scrape_expediente()
        if items:
            await save_items_to_db(items, source_id, db)
            return {"message": f"Scraping completado. Se encontraron {len(items)} items."}
        return {"message": "Scraping completado. No se encontraron nuevos items."}
    elif source.scraper_type == "digesa_pe":
        items = await scrape_digesa()
        if items:
            await save_items_to_db(items, source_id, db)
            return {"message": f"Scraping completado. Se encontraron {len(items)} items."}
        return {"message": "Scraping completado. No se encontraron nuevos items."}
    elif source.scraper_type == "digesa_noticias_pe":
        items = await scrape_digesa_noticias()
        if items:
            await save_items_to_db(items, source_id, db)
            return {"message": f"Scraping completado. Se encontraron {len(items)} items."}
        return {"message": "Scraping completado. No se encontraron nuevos items."}
    elif source.scraper_type == "diputados_noticias_cl":
        items = await scrape_diputados_noticias()
        if items:
            await save_items_to_db(items, source_id, db)
            return {"message": f"Scraping completado. Se encontraron {len(items)} items."}
        return {"message": "Scraping completado. No se encontraron nuevos items."}
    elif source.scraper_type == "diputados_proyectos_cl":
        items = await scrape_diputados_proyectos()
        if items:
            await save_items_to_db(items, source_id, db)
            return {"message": f"Scraping completado. Se encontraron {len(items)} items."}
        return {"message": "Scraping completado. No se encontraron nuevos items."}
    elif source.scraper_type == "ispch_noticias_cl":
        items = await scrape_ispch_noticias()
        if items:
            await save_items_to_db(items, source_id, db)
            return {"message": f"Scraping completado. Se encontraron {len(items)} items."}
        return {"message": "Scraping completado. No se encontraron nuevos items."}
    elif source.scraper_type == "ispch_resoluciones_cl":
        items = await scrape_ispch_resoluciones()
        if items:
            await save_items_to_db(items, source_id, db)
            return {"message": f"Scraping completado. Se encontraron {len(items)} items."}
        return {"message": "Scraping completado. No se encontraron nuevos items."}
    elif source.scraper_type == "minsa_normas_pe":
        items = await scrape_minsa_normas()
        if items:
            await save_items_to_db(items, source_id, db)
            return {"message": f"Scraping completado. Se encontraron {len(items)} items."}
        return {"message": "Scraping completado. No se encontraron nuevos items."}
    elif source.scraper_type == "minsa_noticias_pe":
        items = await scrape_minsa_noticias()
        if items:
            await save_items_to_db(items, source_id, db)
            return {"message": f"Scraping completado. Se encontraron {len(items)} items."}
        return {"message": "Scraping completado. No se encontraron nuevos items."}
    elif source.scraper_type == "senado_noticias_cl":
        items = await scrape_senado_noticias()
        if items:
            await save_items_to_db(items, source_id, db)
            return {"message": f"Scraping completado. Se encontraron {len(items)} items."}
        return {"message": "Scraping completado. No se encontraron nuevos items."}
    elif source.scraper_type == "digemid_noticias_pe":
        items = await scrape_digemid_noticias()
        if items:
            await save_items_to_db(items, source_id, db)
            return {"message": f"Scraping completado. Se encontraron {len(items)} items."}
        return {"message": "Scraping completado. No se encontraron nuevos items."}
    
    raise HTTPException(status_code=400, detail="Tipo de scraper no soportado")

# Variable global para rastrear el estado del scraping
scraping_status = {
    "is_running": False,
    "total_sources": 0,
    "completed_sources": 0,
    "current_source": None,
    "results": []
}

@router.get("/status")
async def get_scraping_status():
    return scraping_status

@router.post("/")
async def scrape_all_sources(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    global scraping_status
    
    # Si ya está corriendo, retornar estado actual
    if scraping_status["is_running"]:
        return {
            "message": "El proceso de scraping ya está en ejecución",
            "status": scraping_status
        }
    
    # Inicializar estado
    sources = db.query(models.Source).filter(models.Source.active == True).all()
    scraping_status.update({
        "is_running": True,
        "total_sources": len(sources),
        "completed_sources": 0,
        "current_source": None,
        "results": []
    })
    
    async def process_sources():
        global scraping_status
        try:
            for source in sources:
                try:
                    scraping_status["current_source"] = source.name
                    
                    # Actualizar timestamp de último scraping
                    source.last_scraped = datetime.utcnow()
                    db.commit()
                    
                    # Ejecutar el scraping
                    result = await trigger_scraping(source.id, background_tasks, db)
                    scraping_status["results"].append({
                        "source": source.name,
                        "status": "success",
                        "message": result.get("message", "Scraping completado")
                    })
                except Exception as e:
                    scraping_status["results"].append({
                        "source": source.name,
                        "status": "error",
                        "message": str(e)
                    })
                
                scraping_status["completed_sources"] += 1
                
        finally:
            scraping_status["is_running"] = False
            scraping_status["current_source"] = None
    
    background_tasks.add_task(process_sources)
    
    return {
        "message": "Proceso de scraping iniciado",
        "status": scraping_status
    }

@router.post("/sources")
async def add_source(
    name: str,
    url: str,
    scraper_type: str,
    db: Session = Depends(get_db)
):
    source = models.Source(
        name=name,
        url=url,
        scraper_type=scraper_type,
        active=True
    )
    db.add(source)
    try:
        db.commit()
        db.refresh(source)
        return source
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/cleanup-duplicates")
async def cleanup_duplicates(db: Session = Depends(get_db)):
    try:
        from sqlalchemy import func
        
        # Encontrar grupos de duplicados basados en URL, título y fecha
        duplicates = db.query(
            models.Item.source_url,
            models.Item.title,
            models.Item.presentation_date,
            func.count(models.Item.id).label('count')
        ).group_by(
            models.Item.source_url,
            models.Item.title,
            models.Item.presentation_date
        ).having(func.count(models.Item.id) > 1).all()
        
        total_deleted = 0
        
        for url, title, date, count in duplicates:
            # Obtener todos los items duplicados para esta combinación
            items = db.query(models.Item).filter(
                models.Item.source_url == url,
                models.Item.title == title,
                models.Item.presentation_date == date
            ).order_by(models.Item.id).all()
            
            if len(items) > 1:
                # Mantener el primer registro (más antiguo) y eliminar el resto
                for item in items[1:]:
                    print(f"Eliminando duplicado - ID: {item.id}, Título: {item.title}, URL: {item.source_url}, Fecha: {item.presentation_date}")
                    db.delete(item)
                    total_deleted += 1
        
        db.commit()
        return {
            "message": f"Se eliminaron {total_deleted} registros duplicados",
            "details": "Se identificaron duplicados basados en URL, título y fecha"
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
