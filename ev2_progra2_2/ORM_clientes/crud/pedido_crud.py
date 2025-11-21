from functools import reduce
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from models import Pedido, Cliente, Menu, MenuIngrediente
from crud.ingrediente_crud import IngredienteCRUD
import datetime

class PedidoCRUD:
    
    @staticmethod
    def procesar_compra(db: Session, cliente_email: str, lista_menus: list, fecha_seleccionada=None):
        """
        Gestiona la transacción completa.
        Ahora acepta 'fecha_seleccionada' para el registro histórico.
        """
        # 1. Validaciones
        cliente = db.query(Cliente).get(cliente_email)
        if not cliente: return False, "Error: Cliente no válido."
        if not lista_menus: return False, "Error: Carrito vacío."

        # 2. Calculo Total
        precios = map(lambda m: m.precio, lista_menus)
        total_compra = reduce(lambda a, b: a + b, precios, 0)

        # 3. Stock
        ingredientes_necesarios = []
        for menu in lista_menus:
            for item in menu.ingredientes_receta:
                ingredientes_necesarios.append((item.ingrediente, item.cantidad_requerida))

        if not IngredienteCRUD.descontar_stock_receta(db, ingredientes_necesarios):
             return False, "Error: Stock insuficiente."

        # 4. Guardar Pedido CON FECHA
        try:
            # Si no nos pasan fecha, usamos la de hoy.
            if not fecha_seleccionada:
                fecha_final = datetime.datetime.now()
            else:
                fecha_final = fecha_seleccionada

            descripcion = f"Compra de {len(lista_menus)} items. Total: ${total_compra}"
            
            # AQUÍ ASIGNAMOS LA FECHA SELECCIONADA
            nuevo_pedido = Pedido(descripcion=descripcion, cliente=cliente, fecha=fecha_final)
            nuevo_pedido.menus = lista_menus 
            
            db.add(nuevo_pedido)
            db.commit()
            db.refresh(nuevo_pedido)

            # 5. Boleta
            items_texto = list(map(lambda m: f"- {m.nombre}: ${m.precio}", lista_menus))
            
            # Formateamos la fecha para la boleta
            fecha_str = fecha_final.strftime('%Y-%m-%d') if hasattr(fecha_final, 'strftime') else str(fecha_final)

            boleta = (
                f"--- BOLETA ---\n"
                f"ID: {nuevo_pedido.id} | Cliente: {cliente.nombre}\n"
                f"Fecha Emisión: {fecha_str}\n"
                f"----------------\n"
                + "\n".join(items_texto) + "\n"
                f"----------------\n"
                f"TOTAL: ${total_compra}"
            )
            return True, boleta

        except SQLAlchemyError as e:
            db.rollback()
            return False, f"Error BD: {str(e)}"

    @staticmethod
    def leer_pedidos(db: Session):
        return db.query(Pedido).options(joinedload(Pedido.menus)).all()

    @staticmethod
    def borrar_pedido_y_restaurar_stock(db: Session, pedido_id: int):
        """
        Borra el pedido y DEVUELVE los ingredientes al stock.
        """
        # Cargar pedido con sus menús e ingredientes (Deep Eager Loading)
        pedido = db.query(Pedido).options(
            joinedload(Pedido.menus).joinedload(Menu.ingredientes_receta).joinedload(MenuIngrediente.ingrediente)
        ).get(pedido_id)

        if not pedido: return False

        try:
            # 1. Devolver Stock
            IngredienteCRUD.devolver_stock_receta(db, pedido.menus)

            # 2. Borrar Pedido
            db.delete(pedido)
            db.commit()
            return True
        except SQLAlchemyError:
            db.rollback()
            return False

    @staticmethod
    def calcular_total_ventas(db: Session):
        pedidos = db.query(Pedido).options(joinedload(Pedido.menus)).all()
        if not pedidos: return 0.0
        
        # Sumar precios de todos los menús de todos los pedidos
        montos = map(lambda p: sum(m.precio for m in p.menus), pedidos)
        return reduce(lambda a, b: a + b, montos, 0.0)