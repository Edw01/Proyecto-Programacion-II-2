from sqlalchemy import Column, String, Integer, Float, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

# Entidad Cliente


class Cliente(Base):
    __tablename__ = 'cliente'
    email = Column(String, primary_key=True)
    nombre = Column(String, nullable=False)
    edad = Column(Integer, nullable=False)
    pedido = relationship(
        "Pedido", back_populates="cliente", uselist=False, cascade="all, delete-orphan")


# Tabla intermedia M:N entre Pedido y Menu (Sin cambios, simple asociación)
pedido_menu = Table('pedido_menu', Base.metadata,
                    Column('pedido_id', Integer, ForeignKey(
                        'pedido.id'), primary_key=True),
                    Column('menu_id', Integer, ForeignKey(
                        'menu.id'), primary_key=True)
                    )

# Cambio con el anterior:
# Se reemplaza la Table simple por un Modelo de Asociación (Association Object)
# Esto permite guardar la "cantidad_requerida" de cada ingrediente para un menu específico.


class MenuIngrediente(Base):
    __tablename__ = 'menu_ingrediente'

    menu_id = Column(Integer, ForeignKey('menu.id'), primary_key=True)
    ingrediente_id = Column(Integer, ForeignKey(
        'ingrediente.id'), primary_key=True)

    # guardar la cantidad
    cantidad_requerida = Column(Float, nullable=False)

    # Relaciones internas
    ingrediente = relationship("Ingrediente")
    menu = relationship("Menu", back_populates="ingredientes_receta")


# Entidad Pedido
class Pedido(Base):
    __tablename__ = 'pedido'
    id = Column(Integer, primary_key=True, autoincrement=True)
    descripcion = Column(String, nullable=False)
    fecha = Column(DateTime, default=datetime.datetime.now)
    cliente_email = Column(String, ForeignKey(
        'cliente.email', onupdate="CASCADE"), nullable=False)
    cliente = relationship("Cliente", back_populates="pedido")
    menus = relationship("Menu", secondary=pedido_menu,
                         back_populates="pedidos")

# Entidad Menu
class Menu(Base):
    __tablename__ = 'menu'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    precio = Column(Integer, nullable=False)

    # Relación hacia la tabla intermedia (Clase de Asociación)
    ingredientes_receta = relationship(
        "MenuIngrediente", back_populates="menu", cascade="all, delete-orphan")

    pedidos = relationship(
        "Pedido", secondary=pedido_menu, back_populates="menus")

# Entidad Ingrediente


class Ingrediente(Base):
    __tablename__ = 'ingrediente'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    # Agregado campo unidad para consistencia
    unidad = Column(String, nullable=False, default="unid")
    # Cambiado a Float para permitir 0.5 kg etc
    cantidad = Column(Float, nullable=False)

    # Relacion inversa con MenuIngrediente
    menus_asociados = relationship(
        "MenuIngrediente", back_populates="ingrediente")
