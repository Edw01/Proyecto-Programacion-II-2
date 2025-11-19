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
        Carga ingredientes desde CSV validando columnas y formato.
        Usa MAP y FILTER para cumplir con la pauta.
        """
        if not os.path.exists(ruta_archivo):
            return "Archivo no encontrado."

        try:
            with open(ruta_archivo, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Validar Columnas Faltantes
                columnas_esperadas = {'nombre', 'unidad', 'cantidad'}
                if not columnas_esperadas.issubset(reader.fieldnames):
                    return "Error: El CSV no tiene las columnas requeridas (nombre, unidad, cantidad)."

                filas = list(reader) # Convertimos a lista para procesar

                # Uso de FILTER para eliminar filas con datos vacíos
                # Filtramos filas donde falte algún dato
                filas_validas = list(filter(lambda row: row['nombre'] and row['unidad'] and row['cantidad'], filas))

                count_agregados = 0
                
                for row in filas_validas:
                    try:
                        nombre = row['nombre'].strip()
                        unidad = row['unidad'].strip()
                        cantidad = float(row['cantidad']) # Validar formato numérico

                        # Verificamos si existe para actualizar O crear (Upsert)
                        ing_existente = db.query(Ingrediente).filter(Ingrediente.nombre.ilike(nombre)).first()
                        
                        if ing_existente:
                            # Actualizamos stock sumando
                            ing_existente.cantidad += cantidad
                        else:
                            # Creamos nuevo
                            nuevo = Ingrediente(nombre=nombre, unidad=unidad, cantidad=cantidad)
                            db.add(nuevo)
                        
                        count_agregados += 1
                    except ValueError:
                        continue # Si la cantidad no es número, saltamos la fila (Control de errores)

                db.commit()
                return f"Proceso completado. Se procesaron {count_agregados} ingredientes."

        except Exception as e:
            db.rollback()
            return f"Error crítico al leer CSV: {str(e)}"