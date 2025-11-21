# Configuración de la base de datos y sesión
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text

# Configuración del motor y la sesión
DATABASE_URL = 'sqlite:///mi_base_de_datos.db'
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa
Base = declarative_base()  # Definimos Base aquí

# Función para obtener la sesión de base de datos
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verificar_conexion():
    """
    Intenta conectar a la base de datos para validar que el motor está activo.
    Retorna True si hay conexión, False si falla.
    """
    try:
        # Creamos una conexión rápida y ejecutamos un comando simple
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Error de conexión a la BD: {e}")
        return False
