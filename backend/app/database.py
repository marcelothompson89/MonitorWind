import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuración dinámica de la URL de la base de datos
SQLALCHEMY_DATABASE_URL = os.getenv(
    "SQLALCHEMY_DATABASE_URL",  # URL de PostgreSQL en producción
    "sqlite:///./monitor_wind.db"  # Por defecto, usa SQLite en local
)

# Si estás usando SQLite, necesitas agregar argumentos especiales
connect_args = {"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}

# Crear el motor de la base de datos
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)

# Configurar la sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

