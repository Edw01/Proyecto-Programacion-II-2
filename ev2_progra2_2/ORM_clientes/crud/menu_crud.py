from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import Menu, Ingrediente, MenuIngrediente
from functools import reduce

class MenuCRUD:

    @staticmethod
    def leer_menus(db: Session):
        # Retorna todos los menús con sus relaciones cargadas.
        return db.query(Menu).all()

    @staticmethod
    def crear_menu(db: Session, nombre: str, descripcion: str, lista_ingredientes: list):
        
        #Crea un menu validando ingredientes y stock usando programación funcional.
        
        #lista_ingredientes: Lista de tuplas o diccionarios 
                            #[(ingrediente_id, cantidad_necesaria), ...]
        
        
        # 1. VALIDACIÓN DE ENTRADA (LAMBDA & FILTER)
        # Filtramos ingredientes con cantidades inválidas (<= 0)
        # lista_ingredientes debe ser [(id, qty), (id, qty)...]
        items_validos = list(filter(lambda item: item[1] > 0, lista_ingredientes))
        
        if len(items_validos) != len(lista_ingredientes):
            print("Error: Se han filtrado ingredientes con cantidad 0 o negativa.")
            if not items_validos: return None

        # Evitar duplicados de ID de ingrediente en la misma receta
        ids_unicos = set()
        items_unicos = []
        for i_id, qty in items_validos:
            if i_id not in ids_unicos:
                ids_unicos.add(i_id)
                items_unicos.append((i_id, qty))
        
        # 2. VALIDACION DE EXISTENCIA Y STOCK EN DB
        # Obtenemos los objetos ingrediente de la DB para verificar
        # ids_unicos contiene los IDs requeridos
        objs_ingredientes = db.query(Ingrediente).filter(Ingrediente.id.in_(ids_unicos)).all()
        
        # Diccionario auxiliar para acceso rapido: {id: ObjetoIngrediente}
        dict_ingredientes = {ing.id: ing for ing in objs_ingredientes}

        # Función Lambda para validar si existe y hay stock suficiente
        # Recibe tupla (id_solicitado, qty_solicitada)
        verificar_stock = lambda item: (
            item[0] in dict_ingredientes and 
            dict_ingredientes[item[0]].cantidad >= item[1]
        )

        # Usamos REDUCE para verificar que TODOS los ingredientes cumplan la condiciOn
        # Devuelve True si todos cumplen, False si alguno falla
        es_posible_crear = reduce(lambda acumulado, item: acumulado and verificar_stock(item), items_unicos, True)

        if not es_posible_crear:
            print("Error: Uno o más ingredientes no existen o no tienen stock suficiente.")
            return None

        # 3. CREACION (MAP)
        try:
            # Instancia del Menu
            nuevo_menu = Menu(nombre=nombre, descripcion=descripcion)
            db.add(nuevo_menu)
            db.flush() # Generar ID del menu antes de insertar detalles

            # Usamos MAP para transformar la lista de tuplas en objetos MenuIngrediente
            receta_objetos = list(map(
                lambda item: MenuIngrediente(
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
            print(f"Error de base de datos al crear menú: {e}")
            return None

    @staticmethod
    def borrar_menu(db: Session, menu_id: int):
        menu = db.query(Menu).get(menu_id)
        if menu:
            db.delete(menu)
            db.commit()
            return True
        return False