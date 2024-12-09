from app.database import SessionLocal, engine, Base
from app.models import models
from datetime import datetime

def init_db():
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear una sesión
    db = SessionLocal()
    
    try:
        # Verificar si la fuente AlertasAnamed_CL ya existe
        anamed_source = db.query(models.Source).filter_by(name="AlertasAnamed_CL").first()
        
        if not anamed_source:
            # Crear la fuente AlertasAnamed_CL
            anamed_source = models.Source(
                name="AlertasAnamed_CL",
                url="https://www.ispch.gob.cl/categorias-alertas/anamed/",
                scraper_type="anamed_cl",
                active=True,
                created_at=datetime.utcnow()
            )
            db.add(anamed_source)
            db.commit()
            print("Fuente AlertasAnamed_CL creada exitosamente")
        else:
            print("La fuente AlertasAnamed_CL ya existe")
            
        # Verificar si la fuente Congreso_PE ya existe
        congreso_source = db.query(models.Source).filter_by(name="Congreso_PE").first()
        
        if not congreso_source:
            # Crear la fuente Congreso_PE
            congreso_source = models.Source(
                name="Congreso_PE",
                url="https://comunicaciones.congreso.gob.pe/?s=&date=&post_type%5B%5D=noticias",
                scraper_type="congreso_pe",
                active=True,
                created_at=datetime.utcnow()
            )
            db.add(congreso_source)
            db.commit()
            print("Fuente Congreso_PE creada exitosamente")
        else:
            print("La fuente Congreso_PE ya existe")

        # Verificar si la fuente Expediente_PE ya existe
        expediente_source = db.query(models.Source).filter_by(name="Expediente_PE").first()
        
        if not expediente_source:
            # Crear la fuente Expediente_PE
            expediente_source = models.Source(
                name="Expediente_PE",
                url="https://wb2server.congreso.gob.pe/spley-portal/#/expediente/search",
                scraper_type="expediente_pe",
                active=True,
                created_at=datetime.utcnow()
            )
            db.add(expediente_source)
            db.commit()
            print("Fuente Expediente_PE creada exitosamente")
        else:
            print("La fuente Expediente_PE ya existe")
            
        # Verificar si la fuente DIGESA_PE ya existe
        digesa_source = db.query(models.Source).filter_by(name="DIGESA_PE").first()
        
        if not digesa_source:
            # Crear la fuente DIGESA_PE
            digesa_source = models.Source(
                name="DIGESA_PE",
                url="http://www.digesa.minsa.gob.pe/noticias/comunicados.asp",
                scraper_type="digesa_pe",
                active=True,
                created_at=datetime.utcnow()
            )
            db.add(digesa_source)
            db.commit()
            print("Fuente DIGESA_PE creada exitosamente")
        else:
            print("La fuente DIGESA_PE ya existe")

        # Verificar si la fuente DIGESA_Noticias_PE ya existe
        digesa_noticias_source = db.query(models.Source).filter_by(name="DIGESA_Noticias_PE").first()
        
        if not digesa_noticias_source:
            # Crear la fuente DIGESA_Noticias_PE
            digesa_noticias_source = models.Source(
                name="DIGESA_Noticias_PE",
                url="http://www.digesa.minsa.gob.pe/noticias/index.asp",
                scraper_type="digesa_noticias_pe",
                active=True,
                created_at=datetime.utcnow()
            )
            db.add(digesa_noticias_source)
            db.commit()
            print("Fuente DIGESA_Noticias_PE creada exitosamente")
        else:
            print("La fuente DIGESA_Noticias_PE ya existe")

        # Verificar si la fuente DiputadosNoticias_CL ya existe
        diputados_source = db.query(models.Source).filter_by(name="DiputadosNoticias_CL").first()
        
        if not diputados_source:
            # Crear la fuente DiputadosNoticias_CL
            diputados_source = models.Source(
                name="DiputadosNoticias_CL",
                url="https://www.camara.cl/cms/noticias/",
                scraper_type="diputados_noticias_cl",
                active=True,
                created_at=datetime.utcnow()
            )
            db.add(diputados_source)
            db.commit()
            print("Fuente DiputadosNoticias_CL creada exitosamente")
        else:
            print("La fuente DiputadosNoticias_CL ya existe")

        # Verificar si la fuente DiputadosProyectos_CL ya existe
        diputados_proyectos_source = db.query(models.Source).filter_by(name="DiputadosProyectos_CL").first()
        
        if not diputados_proyectos_source:
            # Crear la fuente DiputadosProyectos_CL
            diputados_proyectos_source = models.Source(
                name="DiputadosProyectos_CL",
                url="https://www.camara.cl/legislacion/ProyectosDeLey/proyectos_ley.aspx",
                scraper_type="diputados_proyectos_cl",
                active=True,
                created_at=datetime.utcnow()
            )
            db.add(diputados_proyectos_source)
            db.commit()
            print("Fuente DiputadosProyectos_CL creada exitosamente")
        else:
            print("La fuente DiputadosProyectos_CL ya existe")

        # Verificar si la fuente ISPCH_Noticias_CL ya existe
        ispch_noticias_source = db.query(models.Source).filter_by(name="ISPCH_Noticias_CL").first()
        
        if not ispch_noticias_source:
            # Crear la fuente ISPCH_Noticias_CL
            ispch_noticias_source = models.Source(
                name="ISPCH_Noticias_CL",
                url="https://www.ispch.gob.cl/noticia/",
                scraper_type="ispch_noticias_cl",
                active=True,
                created_at=datetime.utcnow()
            )
            db.add(ispch_noticias_source)
            db.commit()
            print("Fuente ISPCH_Noticias_CL creada exitosamente")
        else:
            print("La fuente ISPCH_Noticias_CL ya existe")

        # Verificar si la fuente ISPCH_Resoluciones_CL ya existe
        ispch_resoluciones_source = db.query(models.Source).filter_by(name="ISPCH_Resoluciones_CL").first()
        
        if not ispch_resoluciones_source:
            # Crear la fuente ISPCH_Resoluciones_CL
            ispch_resoluciones_source = models.Source(
                name="ISPCH_Resoluciones_CL",
                url="https://www.ispch.gob.cl/resoluciones/",
                scraper_type="ispch_resoluciones_cl",
                active=True,
                created_at=datetime.utcnow()
            )
            db.add(ispch_resoluciones_source)
            db.commit()
            print("Fuente ISPCH_Resoluciones_CL creada exitosamente")
        else:
            print("La fuente ISPCH_Resoluciones_CL ya existe")

        # Verificar si la fuente MINSA_Normas_PE ya existe
        minsa_normas_source = db.query(models.Source).filter_by(name="MINSA_Normas_PE").first()
        
        if not minsa_normas_source:
            # Crear la fuente MINSA_Normas_PE
            minsa_normas_source = models.Source(
                name="MINSA_Normas_PE",
                url="https://www.gob.pe/institucion/minsa/normas-legales",
                scraper_type="minsa_normas_pe",
                active=True,
                created_at=datetime.utcnow()
            )
            db.add(minsa_normas_source)
            db.commit()
            print("Fuente MINSA_Normas_PE creada exitosamente")
        else:
            print("La fuente MINSA_Normas_PE ya existe")

        # Verificar si la fuente MINSA_Noticias_PE ya existe
        minsa_noticias_source = db.query(models.Source).filter_by(name="MINSA_Noticias_PE").first()
        
        if not minsa_noticias_source:
            # Crear la fuente MINSA_Noticias_PE
            minsa_noticias_source = models.Source(
                name="MINSA_Noticias_PE",
                url="https://www.gob.pe/institucion/minsa/noticias",
                scraper_type="minsa_noticias_pe",
                active=True,
                created_at=datetime.utcnow()
            )
            db.add(minsa_noticias_source)
            db.commit()
            print("Fuente MINSA_Noticias_PE creada exitosamente")
        else:
            print("La fuente MINSA_Noticias_PE ya existe")

        # Verificar si la fuente Senado_Noticias_CL ya existe
        senado_noticias_source = db.query(models.Source).filter_by(name="Senado_Noticias_CL").first()
        
        if not senado_noticias_source:
            # Crear la fuente Senado_Noticias_CL
            senado_noticias_source = models.Source(
                name="Senado_Noticias_CL",
                url="https://www.senado.cl/comunicaciones/noticias",
                scraper_type="senado_noticias_cl",
                active=True,
                created_at=datetime.utcnow()
            )
            db.add(senado_noticias_source)
            db.commit()
            print("Fuente Senado_Noticias_CL creada exitosamente")
        else:
            print("La fuente Senado_Noticias_CL ya existe")

        # Verificar si la fuente DIGEMID_PE ya existe
        digemid_source = db.query(models.Source).filter_by(name="DIGEMID_PE").first()
        
        if not digemid_source:
            # Crear la fuente DIGEMID_PE
            digemid_source = models.Source(
                name="DIGEMID_PE",
                url="https://www.digemid.minsa.gob.pe/webDigemid/?s=",
                scraper_type="digemid_noticias_pe",
                active=True,
                created_at=datetime.utcnow()
            )
            db.add(digemid_source)
            db.commit()
            print("Fuente DIGEMID_PE creada exitosamente")
        else:
            print("La fuente DIGEMID_PE ya existe")

    except Exception as e:
        print(f"Error durante la inicialización: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Inicializando base de datos...")
    init_db()
    print("Inicialización completada")
