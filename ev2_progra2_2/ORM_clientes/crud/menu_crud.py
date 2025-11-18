
from models import Menu
from sqlalchemy.orm import Session

class MenuCRUD:
    def leer_menus(db: Session):
        return db.query(Menu).all()
    
