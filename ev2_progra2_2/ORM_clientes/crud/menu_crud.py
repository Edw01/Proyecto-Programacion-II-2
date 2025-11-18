from models import Menu
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

class MenuCRUD:
    @staticmethod
    def leer_menus(db: Session):
        return db.query(Menu).all()
    
    @staticmethod
    def actualizar_menu(db: Session, id: int, nuevo_nombre:str, nueva_descripcion:str):
        menu = db.query(Menu).filter(Menu.id == id).first()
        if not menu:
            print(f"No se encontró el menú (ID = {id}).")
            return None
        else:
            menu.nombre = nuevo_nombre
            menu.descripcion = nueva_descripcion

            try:
                db.commit()
                db.refresh(menu)
            except SQLAlchemyError as e:
                db.rollback()
                print(f"Error al actualizar el cliente: {e}")
                return None  
            return menu
        

    
