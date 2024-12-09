from app.database import SessionLocal, engine, Base
from app.models import models
from sqlalchemy import text

def update_country_codes():
    print("Iniciando actualización de códigos de país...")
    
    # Crear una sesión
    db = SessionLocal()
    
    try:
        # Actualizar todos los registros que tienen 'PE' como país a 'Perú'
        query = text("UPDATE items SET country = 'Perú' WHERE country = 'PE'")
        result = db.execute(query)
        db.commit()
        
        # Verificar los países después de la actualización
        all_countries = db.query(models.Item.country).distinct().all()
        print(f"Países en la base de datos después de la actualización: {[c[0] for c in all_countries]}")
        
        print("Actualización completada exitosamente")
        
    except Exception as e:
        db.rollback()
        print(f"Error durante la actualización: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Iniciando script de actualización...")
    update_country_codes()
    print("Script completado")
