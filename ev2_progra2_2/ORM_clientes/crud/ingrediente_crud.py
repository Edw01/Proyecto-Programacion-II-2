import re
import csv
import os
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import Ingrediente

class IngredienteCRUD:

    @staticmethod
    def crear_ingrediente(db: Session, nombre: str, unidad: str, cantidad: float):
        # Validar nombre no vacío y stock positivo con LAMBDA
        validar_datos = lambda n, c: len(n.strip()) > 0 and c >= 0
        
        if not validar_datos(nombre, cantidad):
            print(f"Error: Datos inválidos para '{nombre}'.")
            return None

        # Verificar duplicados
        if db.query(Ingrediente).filter(Ingrediente.nombre.ilike(nombre)).first():
            print(f"El ingrediente '{nombre}' ya existe.")
            return None

        nuevo = Ingrediente(nombre=nombre, unidad=unidad, cantidad=float(cantidad))
        db.add(nuevo)
        try:
            db.commit()
            db.refresh(nuevo)
            return nuevo
        except SQLAlchemyError:
            db.rollback()
            return None

    @staticmethod
    def leer_ingredientes(db: Session):
        return db.query(Ingrediente).all()

    @staticmethod
    def borrar_ingrediente(db: Session, ingrediente_id: int):
        ing = db.query(Ingrediente).get(ingrediente_id)
        if ing:
            db.delete(ing)
            db.commit()
            return True
        return False

    @staticmethod
    def obtener_ingredientes_bajo_stock(db: Session, umbral: float = 5.0):
        todos = db.query(Ingrediente).all()
        # Uso de FILTER
        return list(filter(lambda ing: ing.cantidad <= umbral, todos))

    # --- CARGA MASIVA CSV ---
    @staticmethod
    def cargar_masivamente_desde_csv(db: Session, ruta_archivo: str):
        """
        Carga ingredientes desde CSV.
        Maneja BOM (utf-8-sig) y espacios en las cabeceras.
        """
        if not os.path.exists(ruta_archivo):
            return "Archivo no encontrado."

        try:
            # Usamos 'utf-8-sig' para leer archivos creados en Excel/Windows correctamente
            with open(ruta_archivo, mode='r', encoding='utf-8-sig') as f:
                
                # Leemos primero para detectar el separador automáticamente (coma o punto y coma)
                sample = f.read(1024)
                f.seek(0)
                dialect = csv.Sniffer().sniff(sample)
                
                reader = csv.DictReader(f, dialect=dialect)
                
                # Normalizar cabeceras (quitar espacios extra y convertir a minúsculas)
                # Esto arregla si el CSV dice " nombre " o "Nombre"
                if reader.fieldnames:
                    reader.fieldnames = [col.strip().lower() for col in reader.fieldnames]

                # Validar Columnas
                columnas_requeridas = {'nombre', 'unidad', 'cantidad'}
                columnas_en_csv = set(reader.fieldnames)

                if not columnas_requeridas.issubset(columnas_en_csv):
                    return f"Error: Faltan columnas. El CSV tiene: {list(columnas_en_csv)}"

                # Convertimos a lista para aplicar Filter
                filas = list(reader) 

                # Filtrar filas vacías
                filas_validas = list(filter(lambda row: row.get('nombre') and row.get('cantidad'), filas))

                count_agregados = 0
                count_actualizados = 0
                
                for row in filas_validas:
                    try:
                        nombre = row['nombre'].strip()
                        unidad = row['unidad'].strip()
                        # Reemplazar coma por punto si el Excel guardó decimales como "10,5"
                        cant_str = row['cantidad'].replace(',', '.')
                        cantidad = float(cant_str)

                        # Lógica de Upsert (Actualizar o Crear)
                        ing_existente = db.query(Ingrediente).filter(Ingrediente.nombre.ilike(nombre)).first()
                        
                        if ing_existente:
                            ing_existente.cantidad += cantidad
                            count_actualizados += 1
                        else:
                            nuevo = Ingrediente(nombre=nombre, unidad=unidad, cantidad=cantidad)
                            db.add(nuevo)
                            count_agregados += 1
                    
                    except ValueError:
                        continue # Saltar filas con errores numéricos

                db.commit()
                return f"Éxito: {count_agregados} nuevos, {count_actualizados} actualizados."

        except Exception as e:
            db.rollback()
            return f"Error crítico: {str(e)}"