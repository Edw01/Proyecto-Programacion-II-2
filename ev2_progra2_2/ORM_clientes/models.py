# Definición de modelos clases etc.
from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

class Cliente(Base):
    __tablename__ = 'clientes'
    email = Column(String, primary_key=True)  # Email como clave primaria
    nombre = Column(String, nullable=False)
    edad= Column(Integer, nullable=False)
    pedidos = relationship("Pedido", back_populates="cliente", cascade="all, delete-orphan")


pedidos_menus = Table('pedidos_menus',
                      Column('pedido_id', Integer, ForeignKey('pedidos.id'), primary_key=True),
                      Column('menu_id', Integer, ForeignKey('menus.id'), primary_key=True)
)

menus_ingredientes = Table(('menus_ingredientes'),
                        Column('menu_id', Integer, ForeignKey('menus.id'), primary_key=True),
                        Column('ingrediente_id', Integer, ForeignKey('ingredientes.id'), primary_key=True)
)

class Pedido(Base):
    __tablename__ = 'pedidos'

    id = Column(Integer, primary_key=True, autoincrement=True )
    descripcion = Column(String, nullable=False)
    cliente_email = Column(String, ForeignKey('clientes.email', onupdate="CASCADE"), nullable=False)
    cliente = relationship("Cliente", back_populates="pedidos")
    menus = relationship("Menu", secondary=pedidos_menus, back_populates="pedidos")

class Menu(Base):
    __tablename__ = 'menus'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    pedidos = relationship("Pedido", secondary=pedidos_menus, back_populates="menus")
    ingredientes = relationship("Ingrediente", secondary=menus_ingredientes, back_populates="menus")


class Ingrediente(Base):
    __tablename__ = 'ingredientes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    cantidad = Column(Integer, nullable=False)
    menus = relationship("Menu", secondary=menus_ingredientes, back_populates="ingredientes")


