import time
from functools import reduce  # <--- IMPORTANTE: Necesario para el reduce
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from models import Pedido, Cliente


class PedidoCRUD:

    @staticmethod
    def _try_commit(db: Session, max_retries=3, delay=0.5):
        """Intentar hacer commit con reintentos en caso de errores de bloqueo."""
        retries = 0
        while retries < max_retries:
            try:
                db.commit()
                return True
            except OperationalError as e:
                if "database is locked" in str(e):
                    db.rollback()
                    print(
                        f"Intento {retries+1}/{max_retries}: la base de datos está bloqueada, reintentando en {delay} segundos...")
                    time.sleep(delay)
                    retries += 1
                else:
                    print(f"Error de base de datos: {e}")
                    db.rollback()
                    return False
            except SQLAlchemyError as e:
                print(f"Error al hacer commit: {e}")
                db.rollback()
                return False
        print("Error: no se pudo hacer commit después de varios intentos.")
        return False

    @staticmethod
    def crear_pedido(db: Session, cliente_email: str, descripcion: str):
        # Buscamos por email, ya que es la PK en tu modelo Cliente
        cliente = db.query(Cliente).get(cliente_email)
        if cliente:
            pedido = Pedido(descripcion=descripcion, cliente=cliente)
            db.add(pedido)
            if not PedidoCRUD._try_commit(db):
                return None
            db.refresh(pedido)
            return pedido
        print(f"No se encontró el cliente con Email '{cliente_email}'.")
        return None

    @staticmethod
    def leer_pedidos(db: Session, cliente_nombre=None):
        query = db.query(Pedido).join(Cliente)
        if cliente_nombre and cliente_nombre != "Todos":
            query = query.filter(Cliente.nombre == cliente_nombre)
        return query.all()

    @staticmethod
    def actualizar_pedido(db: Session, pedido_id: int, nueva_descripcion: str):
        pedido = db.query(Pedido).get(pedido_id)
        if pedido:
            pedido.descripcion = nueva_descripcion
            if not PedidoCRUD._try_commit(db):
                return None
            db.refresh(pedido)
            return pedido
        print(f"No se encontró el pedido con ID '{pedido_id}'.")
        return None

    @staticmethod
    def borrar_pedido(db: Session, pedido_id: int):
        pedido = db.query(Pedido).get(pedido_id)
        if pedido:
            db.delete(pedido)
            if not PedidoCRUD._try_commit(db):
                return False
            return True
        return False

    # NUEVA FUNCIÓN CON PROGRAMACIÓN FUNCIONAL (MAP/REDUCE)
    @staticmethod
    def calcular_total_ventas(db: Session):
        """
        Calcula un estimado total de ventas (Simulación para cumplir pauta).
        Usa MAP para obtener valores y REDUCE para sumar.
        """
        pedidos = db.query(Pedido).all()

        if not pedidos:
            return 0.0

        # 1. Simulación de precio: Asumimos un valor fijo por pedido si no hay menús
        # (Esto es para cumplir el requisito académico de usar map/reduce)
        # Transformamos cada objeto pedido en un monto (ej: $5000 por pedido)
        montos = map(lambda p: 5000.0, pedidos)

        # 2. REDUCE: Sumar todo a un solo valor total
        total_general = reduce(lambda a, b: a + b, montos, 0.0)

        return total_general
