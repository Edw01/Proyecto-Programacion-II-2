from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from models import Menu, Ingrediente, MenuIngrediente
from functools import reduce

class MenuCRUD:
    @staticmethod
    def leer_menus(db: Session):
        """
        Retorna todos los menús cargando INMEDIATAMENTE sus ingredientes (Eager Loading).
        Esto evita el error 'DetachedInstanceError' al cerrar la sesión.
        """
        # Usamos joinedload para traer las relaciones en la misma consulta
        return db.query(Menu).options(
            joinedload(Menu.ingredientes_receta).joinedload(MenuIngrediente.ingrediente)
        ).all()

    @staticmethod
    def crear_menu(db: Session, nombre: str, descripcion: str, lista_ingredientes: list):
        
        #Crea un menu validando ingredientes y stock usando programación funcional.
        
        #lista_ingredientes: Lista de tuplas o diccionarios 
                            #[(ingrediente_id, cantidad_necesaria), ...]
        
        # Filtramos ingredientes con cantidades inválidas (<= 0)
        # lista_ingredientes debe ser [(id, qty), (id, qty)...]
        # 1. VALIDACIÓN DE ENTRADA (LAMBDA & FILTER)
        items_validos = list(filter(lambda item: item[1] > 0, lista_ingredientes))
        if len(items_validos) != len(lista_ingredientes):
            if not items_validos: return None

        ids_unicos = set()
        items_unicos = []
        for i_id, qty in items_validos:
            if i_id not in ids_unicos:
                ids_unicos.add(i_id)
                items_unicos.append((i_id, qty))
        
        objs_ingredientes = db.query(Ingrediente).filter(Ingrediente.id.in_(ids_unicos)).all()
        dict_ingredientes = {ing.id: ing for ing in objs_ingredientes}

        verificar_stock = lambda item: (
            item[0] in dict_ingredientes and 
            dict_ingredientes[item[0]].cantidad >= item[1]
        )

        es_posible_crear = reduce(lambda acumulado, item: acumulado and verificar_stock(item), items_unicos, True)

        if not es_posible_crear:
            print("Error: Stock insuficiente.")
            return None

        # 3. CREACION 
        try:
            nuevo_menu = Menu(nombre=nombre, descripcion=descripcion)
            db.add(nuevo_menu)
            db.flush() 

            # CORRECCIÓN: Usamos MenuIngrediente (Clase) en lugar de menu_ingrediente (Tabla)
            receta_objetos = list(map(
                lambda item: MenuIngrediente( # <--- MAYÚSCULAS, es una Clase
                    menu_id=nuevo_menu.id,
                    ingrediente_id=item[0],
                    cantidad_requerida=item[1]
                ),
                items_unicos
            ))

            db.add_all(receta_objetos)
            db.commit()
            db.refresh(nuevo_menu)
            return nuevo_menu

        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error: {e}")
            return None

    @staticmethod
    def borrar_menu(db: Session, menu_id: int):
        menu = db.query(Menu).get(menu_id)
        if menu:
            db.delete(menu)
            db.commit()
            return True
        return False