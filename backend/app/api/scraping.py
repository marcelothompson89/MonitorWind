from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from datetime import datetime
import asyncio
import json

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

async def save_items_to_db(items, db: Session):
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

# Estado global del proceso de scraping
scraping_status = {
    "is_running": False,
    "total_sources": 0,
    "completed_sources": 0,
    "current_source": None,
    "start_time": None,
    "results": []
}

async def status_event_generator():
    global scraping_status
    while scraping_status["is_running"]:
        # Crear el mensaje de estado
        status_data = {
            "is_running": scraping_status["is_running"],
            "total_sources": scraping_status["total_sources"],
            "completed_sources": scraping_status["completed_sources"],
            "current_source": scraping_status["current_source"],
            "results": scraping_status["results"]
        }
        
        # Enviar el mensaje como evento SSE
        yield f"data: {json.dumps(status_data)}\n\n"
        
        # Esperar un poco antes de enviar la siguiente actualización
        await asyncio.sleep(0.5)
    
    # Enviar un último mensaje cuando el proceso termina
    final_status = {
        "is_running": False,
        "total_sources": scraping_status["total_sources"],
        "completed_sources": scraping_status["completed_sources"],
        "results": scraping_status["results"]
    }
    yield f"data: {json.dumps(final_status)}\n\n"

@router.get("/scraping/status/stream")
async def stream_status():
    return StreamingResponse(
        status_event_generator(),
        media_type="text/event-stream"
    )

@router.get("/scraping/status")
async def get_scraping_status():
    """
    Endpoint para consultar el estado actual del proceso de scraping.
    """
    global scraping_status
    print(f"Estado actual: {scraping_status}")
    return {
        "is_running": scraping_status["is_running"],
        "total_sources": scraping_status["total_sources"],
        "completed_sources": scraping_status["completed_sources"],
        "current_source": scraping_status["current_source"],
        "results": scraping_status["results"]
    }

@router.post("/scraping", include_in_schema=True)
@router.post("/scraping/", include_in_schema=True)
async def scrape_all_sources(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    global scraping_status
    
    # Si ya está corriendo, retornar estado actual
    if scraping_status["is_running"]:
        print("Scraping ya en ejecución")
        return {
            "message": "El proceso de scraping ya está en ejecución",
            "is_running": True,
            "total_sources": scraping_status["total_sources"],
            "completed_sources": scraping_status["completed_sources"],
            "current_source": scraping_status["current_source"]
        }
    
    # Lista de scrapers disponibles
    scrapers = [
        ("ANAMED", scrape_anamed),
        ("Congreso PE", scrape_congreso),
        ("Expediente PE", scrape_expediente),
        ("DIGESA", scrape_digesa),
        ("DIGESA Noticias", scrape_digesa_noticias),
        ("Diputados Noticias", scrape_diputados_noticias),
        ("Diputados Proyectos", scrape_diputados_proyectos),
        ("ISPCH Noticias", scrape_ispch_noticias),
        ("ISPCH Resoluciones", scrape_ispch_resoluciones),
        ("MINSA Normas", scrape_minsa_normas),
        ("MINSA Noticias", scrape_minsa_noticias),
        ("Senado Noticias", scrape_senado_noticias),
        ("DIGEMID Noticias", scrape_digemid_noticias)
    ]
    
    print("Iniciando nuevo proceso de scraping")
    # Inicializar estado
    scraping_status.update({
        "is_running": True,
        "total_sources": len(scrapers),
        "completed_sources": 0,
        "current_source": None,
        "results": []
    })
    
    async def process_sources():
        global scraping_status
        try:
            for name, scraper_func in scrapers:
                try:
                    scraping_status["current_source"] = name
                    print(f"[{scraping_status['completed_sources'] + 1}/{len(scrapers)}] Iniciando scraping de {name}")
                    
                    # Ejecutar el scraping
                    items = await scraper_func()
                    if items:
                        await save_items_to_db(items, db)
                        scraping_status["results"].append({
                            "source": name,
                            "status": "success",
                            "message": f"Scraping completado. Se encontraron {len(items)} items."
                        })
                        print(f"✓ {name}: {len(items)} items encontrados")
                    else:
                        scraping_status["results"].append({
                            "source": name,
                            "status": "success",
                            "message": "No se encontraron nuevos items."
                        })
                        print(f"✓ {name}: No se encontraron items")
                except Exception as e:
                    print(f"✗ Error en {name}: {str(e)}")
                    scraping_status["results"].append({
                        "source": name,
                        "status": "error",
                        "message": str(e)
                    })
                
                scraping_status["completed_sources"] += 1
                print(f"Progreso: {scraping_status['completed_sources']}/{scraping_status['total_sources']}")
                
        finally:
            print("Finalizando proceso de scraping")
            scraping_status["is_running"] = False
            scraping_status["current_source"] = None
    
    background_tasks.add_task(process_sources)
    
    return {
        "message": "Proceso de scraping iniciado",
        "is_running": True,
        "total_sources": len(scrapers),
        "completed_sources": 0,
        "current_source": None
    }

@router.post("/cleanup")
async def cleanup_duplicates(db: Session = Depends(get_db)):
    try:
        # Encontrar duplicados basados en URL
        url_duplicates = db.query(
            models.Item.source_url,
            func.count(models.Item.id).label('count'),
            func.min(models.Item.id).label('min_id')
        ).group_by(
            models.Item.source_url
        ).having(
            func.count(models.Item.id) > 1
        ).all()
        
        # Encontrar duplicados basados en título y fecha
        title_date_duplicates = db.query(
            models.Item.title,
            models.Item.presentation_date,
            func.count(models.Item.id).label('count'),
            func.min(models.Item.id).label('min_id')
        ).group_by(
            models.Item.title,
            models.Item.presentation_date
        ).having(
            func.count(models.Item.id) > 1
        ).all()
        
        total_deleted = 0
        
        # Eliminar duplicados por URL
        for url, count, min_id in url_duplicates:
            items_to_delete = db.query(models.Item).filter(
                models.Item.source_url == url,
                models.Item.id != min_id
            ).all()
            
            for item in items_to_delete:
                print(f"Eliminando duplicado - ID: {item.id}, Título: {item.title}, URL: {item.source_url}, Fecha: {item.presentation_date}")
                db.delete(item)
                total_deleted += 1
        
        # Eliminar duplicados por título y fecha
        for title, date, count, min_id in title_date_duplicates:
            items_to_delete = db.query(models.Item).filter(
                models.Item.title == title,
                models.Item.presentation_date == date,
                models.Item.id != min_id
            ).all()
            
            for item in items_to_delete:
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
        raise HTTPException(
            status_code=500,
            detail=f"Error al limpiar duplicados: {str(e)}"
        )
