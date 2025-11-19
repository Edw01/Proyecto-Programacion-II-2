from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import Ingrediente
# Importamos reduce si quisieras hacer cálculos complejos, pero usaremos filter y lambda aquí
from functools import reduce 

class IngredienteCRUD:

    @staticmethod
    def crear_ingrediente(db: Session, nombre: str, unidad: str, cantidad: float):
        """
        Crea un nuevo ingrediente validando los datos con Lambdas.
        """
        # Validamos que la cantidad no sea negativa y el nombre no esté vacío
        validar_datos = lambda n, c: len(n.strip()) > 0 and c >= 0
        
        if not validar_datos(nombre, cantidad):
            print(f"Error: Datos inválidos para el ingrediente '{nombre}'.")
            return None
        # ------------------------------------------------------

        # Verificar si ya existe (ignorando mayúsculas/minúsculas)
        ingrediente_existente = db.query(Ingrediente).filter(Ingrediente.nombre.ilike(nombre)).first()
        if ingrediente_existente:
            print(f"El ingrediente '{nombre}' ya existe.")
            return ingrediente_existente

        nuevo_ingrediente = Ingrediente(nombre=nombre, unidad=unidad, cantidad=float(cantidad))
        db.add(nuevo_ingrediente)
        
        try:
            db.commit()
            db.refresh(nuevo_ingrediente)
            return nuevo_ingrediente
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error al crear ingrediente: {e}")
            return None

    @staticmethod
    def leer_ingredientes(db: Session):
        """Devuelve todos los ingredientes."""
        return db.query(Ingrediente).all()

    @staticmethod
    def obtener_ingrediente_por_id(db: Session, ingrediente_id: int):
        return db.query(Ingrediente).get(ingrediente_id)

    @staticmethod
    def actualizar_stock(db: Session, ingrediente_id: int, cantidad_a_sumar: float):
        """
        Actualiza el stock sumando (o restando si es negativo) la cantidad.
        """
        ingrediente = db.query(Ingrediente).get(ingrediente_id)
        
        if ingrediente:
            nueva_cantidad = ingrediente.cantidad + cantidad_a_sumar
            
            # Validación simple para no dejar stock negativo
            if nueva_cantidad < 0:
                print(f"Error: No hay suficiente stock de '{ingrediente.nombre}'.")
                return None

            ingrediente.cantidad = float(nueva_cantidad)
            try:
                db.commit()
                db.refresh(ingrediente)
                return ingrediente
            except SQLAlchemyError as e:
                db.rollback()
                print(f"Error al actualizar stock: {e}")
                return None
        return None

    @staticmethod
    def borrar_ingrediente(db: Session, ingrediente_id: int):
        ingrediente = db.query(Ingrediente).get(ingrediente_id)
        if ingrediente:
            db.delete(ingrediente)
            try:
                db.commit()
                return True
            except SQLAlchemyError as e:
                db.rollback()
                print(f"Error al borrar ingrediente: {e}")
                return False
        return False

    @staticmethod
    def obtener_ingredientes_bajo_stock(db: Session, umbral: float = 5.0):
        """
        Retorna una lista de ingredientes con stock menor al umbral.
        USA FILTER Y LAMBDA
        """
        todos = db.query(Ingrediente).all()
        
        # Filtramos la lista usando programación funcional en lugar de un bucle for
        bajos_en_stock = list(filter(lambda ing: ing.cantidad <= umbral, todos))
        # -----------------------------------------------
        
        return bajos_en_stock