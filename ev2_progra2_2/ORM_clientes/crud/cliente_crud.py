import re
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import Cliente

class ClienteCRUD:
    @staticmethod
    def crear_cliente(db: Session, nombre: str, email: str, edad: int):
        """
        Crea un nuevo cliente validando edad y email con Lambdas, Filter y Map.
        """
        
        # 1. USAMOS MAP: Normalizar datos (Nombre 'Titulo', Email minúsculas)
        # Transformamos los datos de entrada antes de validar
        datos_crudos = [nombre, email]
        nombre_fmt, email_fmt = list(map(lambda x: x.strip().title() if '@' not in x else x.strip().lower(), datos_crudos))

        # 2. USAMOS LAMBDA & FILTER: Validación
        validar_edad = lambda e: e >= 18
        validar_email = lambda m: re.match(r"[^@]+@[^@]+\.[^@]+", m) is not None

        # Empaquetamos para filtrar
        datos_a_validar = [(nombre_fmt, email_fmt, edad)]
        
        datos_validos = list(filter(lambda x: validar_email(x[1]) and validar_edad(x[2]), datos_a_validar))

        if not datos_validos:
            print("Error: Cliente debe ser mayor de 18 y tener email válido.")
            return None

        # 3. Verificar unicidad (Requisito Rúbrica)
        if db.query(Cliente).filter_by(email=email_fmt).first():
            print(f"El cliente '{email_fmt}' ya existe.")
            return None

        # 4. Crear y Guardar
        cliente = Cliente(nombre=nombre_fmt, email=email_fmt, edad=edad)
        db.add(cliente)
        try:
            db.commit()
            db.refresh(cliente)
            return cliente
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error DB: {e}")
            return None

    @staticmethod
    def leer_clientes(db: Session):
        return db.query(Cliente).all()

    @staticmethod
    def actualizar_cliente(db: Session, email_actual: str, nuevo_nombre: str, nuevo_email: str, edad: int):
        cliente = db.query(Cliente).get(email_actual)
        if not cliente: return None

        # Si cambia el ID (Email), es complejo por las FKs, simplificamos actualizando otros campos
        # o implementando lógica de borrado/creación si no tiene pedidos.
        
        # Aquí simplificamos actualización básica
        cliente.nombre = nuevo_nombre.strip().title()
        cliente.edad = int(edad)
        # Nota: Actualizar la PK (email) suele requerir cascade updates en BD o recrear.
        
        try:
            db.commit()
            db.refresh(cliente)
            return cliente
        except SQLAlchemyError:
            db.rollback()
            return None

    @staticmethod
    def borrar_cliente(db: Session, email: str):
        """
        Elimina un cliente SOLO SI no tiene pedidos asociados.
        """
        cliente = db.query(Cliente).get(email)
        if not cliente:
            return "No encontrado"
        
        # Accedemos a la relación 'pedido' definida en models.py
        if len(cliente.pedido) > 0:
            print(f"Error: Cliente {email} tiene pedidos activos.")
            return "Tiene Pedidos" # Retornamos un código especial

        db.delete(cliente)
        try:
            db.commit()
            return "OK"
        except SQLAlchemyError as e:
            db.rollback()
            return "Error BD"
