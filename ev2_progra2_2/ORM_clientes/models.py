from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

# 1. CLASE DE ASOCIACIÓN
class MenuIngrediente(Base):
    __tablename__ = 'menu_ingrediente'

    menu_id = Column(Integer, ForeignKey('menu.id'), primary_key=True)
    ingrediente_id = Column(Integer, ForeignKey('ingrediente.id'), primary_key=True)
    
    # guardar la cantidad
    cantidad_requerida = Column(Float, nullable=False)

    # Relaciones internas
    ingrediente = relationship("Ingrediente")
    menu = relationship("Menu", back_populates="ingredientes_receta")

# 2. Entidad Cliente 
class Cliente(Base):
    __tablename__ = 'cliente'
    email = Column(String, primary_key=True)
    nombre = Column(String, nullable=False)
    edad = Column(Integer, nullable=False)
    pedido = relationship("Pedido", back_populates="cliente", cascade="all, delete-orphan")

# 3. Entidad Ingrediente
class Ingrediente(Base):
    __tablename__ = 'ingrediente'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    unidad = Column(String, nullable=False)
    cantidad = Column(Float, nullable=False)

# 4. Entidad Menu 
class Menu(Base):
    __tablename__ = 'menu'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    
    # Relación hacia la tabla intermedia (Clase de Asociación)
    ingredientes_receta = relationship("MenuIngrediente", back_populates="menu", cascade="all, delete-orphan")

# 5. Entidad Pedido 
class Pedido(Base):
    __tablename__ = 'pedido'
    id = Column(Integer, primary_key=True, autoincrement=True)
    descripcion = Column(String, nullable=False)
    fecha = Column(DateTime, default=datetime.datetime.now)
    cliente_email = Column(String, ForeignKey('cliente.email', onupdate="CASCADE"), nullable=False)
    cliente = relationship("Cliente", back_populates="pedido")
    