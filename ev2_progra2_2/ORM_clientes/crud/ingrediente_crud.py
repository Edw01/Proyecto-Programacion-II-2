from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import Ingrediente

class IngredienteCRUD:

    @staticmethod
    def crear_ingrediente(db: Session, nombre: str, unidad: str, cantidad: float):
        # 1. Validación funcional
        validar_datos = lambda n, c: len(n.strip()) > 0 and c >= 0
        
        if not validar_datos(nombre, cantidad):
            print(f"Error: Datos inválidos para '{nombre}'.")
            return None

        # 2. Upsert (Actualizar si existe)
        ingrediente_existente = db.query(Ingrediente).filter(Ingrediente.nombre.ilike(nombre)).first()
        
        if ingrediente_existente:
            ingrediente_existente.cantidad += float(cantidad)
            try:
                db.commit()
                db.refresh(ingrediente_existente)
                return ingrediente_existente
            except SQLAlchemyError:
                db.rollback()
                return None

        # 3. Crear nuevo
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
        return list(filter(lambda ing: ing.cantidad <= umbral, todos))
    
    # --- FUNCIONES TRANSACCIONALES (Las que faltaban) ---

    @staticmethod
    def descontar_stock_receta(db: Session, lista_ingredientes_requeridos: list):
        """
        Recibe: [(ingrediente_obj, cantidad_necesaria), ...]
        Resta el stock. Retorna True si tuvo éxito, False si faltó stock.
        """
        # 1. Verificar stock de TODO primero
        for ing, cant_req in lista_ingredientes_requeridos:
            if ing.cantidad < cant_req:
                return False
        
        # 2. Si todo alcanza, descontamos
        for ing, cant_req in lista_ingredientes_requeridos:
            ing.cantidad -= float(cant_req)
        
        return True

    @staticmethod
    def devolver_stock_receta(db: Session, lista_menus: list):
        """
        Recibe una lista de objetos Menu.
        Recorre sus ingredientes y suma el stock de vuelta.
        """
        for menu in lista_menus:
            # Accedemos a la tabla intermedia MenuIngrediente
            for item in menu.ingredientes_receta:
                ingrediente = item.ingrediente 
                cantidad_a_devolver = item.cantidad_requerida
                
                ingrediente.cantidad += float(cantidad_a_devolver)