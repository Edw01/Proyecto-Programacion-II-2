# Definición de modelos clases etc.
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

# Entidad Cliente
class Cliente(Base):
    __tablename__ = 'cliente'
    email = Column(String, primary_key=True)  # Email como clave primaria
    nombre = Column(String, nullable=False)
    edad = Column(Integer, nullable=False)
    pedido = relationship(
        "Pedido", back_populates="cliente", cascade="all, delete-orphan")


# Tabla intermedia M:N entre Pedido y Menu
pedido_menu = Table('pedido_menu', Base.metadata,
                    Column('pedido_id', Integer, ForeignKey(
                        'pedido.id'), primary_key=True),
                    Column('menu_id', Integer, ForeignKey(
                        'menu.id'), primary_key=True)
                    )

# Tabla intermedia M:N entre Menu e Ingrediente
menu_ingrediente = Table(('menu_ingrediente'), Base.metadata,
                         Column('menu_id', Integer, ForeignKey(
                             'menu.id'), primary_key=True),
                         Column('ingrediente_id', Integer, ForeignKey(
                             'ingrediente.id'), primary_key=True)
                         )

# Entidad Pedido
class Pedido(Base):
    __tablename__ = 'pedido'

    id = Column(Integer, primary_key=True, autoincrement=True)
    descripcion = Column(String, nullable=False)
    cliente_email = Column(String, ForeignKey(
        'cliente.email', onupdate="CASCADE"), nullable=False)
    cliente = relationship("Cliente", back_populates="pedido")
    menu = relationship("Menu", secondary=pedido_menu, back_populates="")

# Entidad Menu
class Menu(Base):
    __tablename__ = 'menu'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    pedidos = relationship(
        "Pedido", secondary=pedido_menu, back_populates="menu")
    ingrediente = relationship(
        "Ingrediente", secondary=menu_ingrediente, back_populates="menu")

# Entidad Ingrediente
class Ingrediente(Base):
    __tablename__ = 'ingrediente'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    unidad = Column(String, nullable=False)
    cantidad = Column(Integer, nullable=False)
    menu = relationship("Menu", secondary=menu_ingrediente,
                        back_populates="ingrediente")
