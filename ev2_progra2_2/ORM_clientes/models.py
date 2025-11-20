from sqlalchemy import Column, String, Integer, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

# Entidad Cliente
class Cliente(Base):
    __tablename__ = 'cliente'
    email = Column(String, primary_key=True)
    nombre = Column(String, nullable=False)
    edad = Column(Integer, nullable=False)
    pedido = relationship(
        "Pedido", back_populates="cliente", cascade="all, delete-orphan")

# Tabla intermedia M:N entre Pedido y Menu (Sin cambios, simple asociación)
pedido_menu = Table('pedido_menu', Base.metadata,
                    Column('pedido_id', Integer, ForeignKey('pedido.id'), primary_key=True),
                    Column('menu_id', Integer, ForeignKey('menu.id'), primary_key=True)
                    )

# Cambio con el anterior:
# Se reemplaza la Table simple por un Modelo de Asociación (Association Object)
# Esto permite guardar la "cantidad_requerida" de cada ingrediente para un menu específico.

class MenuIngrediente(Base):
    __tablename__ = 'menu_ingrediente'
    
    menu_id = Column(Integer, ForeignKey('menu.id'), primary_key=True)
    ingrediente_id = Column(Integer, ForeignKey('ingrediente.id'), primary_key=True)
    
    # Cantidad necesaria para la receta (por ej: 0.5 para media palta)
    cantidad_requerida = Column(Float, nullable=False)

    # Relaciones bidireccionales
    ingrediente = relationship("Ingrediente", back_populates="menus_asociados")
    menu = relationship("Menu", back_populates="ingredientes_asociados")


# Entidad Pedido
class Pedido(Base):
    __tablename__ = 'pedido'

    id = Column(Integer, primary_key=True, autoincrement=True)
    descripcion = Column(String, nullable=False)
    cliente_email = Column(String, ForeignKey('cliente.email', onupdate="CASCADE"), nullable=False)
    
    cliente = relationship("Cliente", back_populates="pedido")
    menu = relationship("Menu", secondary=pedido_menu, back_populates="pedidos")

# Entidad Menu
class Menu(Base):
    __tablename__ = 'menu'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    
    pedidos = relationship("Pedido", secondary=pedido_menu, back_populates="menu")
    
    # Relacion con MenuIngrediente (Asociation Object)
    ingredientes_asociados = relationship("MenuIngrediente", back_populates="menu", cascade="all, delete-orphan")

# Entidad Ingrediente
class Ingrediente(Base):
    __tablename__ = 'ingrediente'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    unidad = Column(String, nullable=False)
    cantidad = Column(Integer, nullable=False)
    menu = relationship("Menu", secondary=menu_ingrediente,
                        back_populates="ingrediente")
