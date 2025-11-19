import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sqlalchemy.orm import Session
from models import Ingrediente
import customtkinter as ctk

def mostrar_grafico_stock(frame_padre, db: Session):
    
    # Genera un grafico de barras incrustado en Tkinter mostrando el stock actual.
    
    # Obtener datos
    ingredientes = db.query(Ingrediente).all()
    
    if not ingredientes:
        lbl = ctk.CTkLabel(frame_padre, text="No hay datos para graficar")
        lbl.pack()
        return

    nombres = [i.nombre for i in ingredientes]
    cantidades = [i.cantidad for i in ingredientes]

    # Crear figura
    fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
    
    # Colores condicionales (Rojo si stock < 5 para mejor visualizacion)
    colores = ['red' if c < 5 else 'skyblue' for c in cantidades]
    
    ax.bar(nombres, cantidades, color=colores)
    ax.set_title("Nivel de Stock por Ingrediente")
    ax.set_ylabel("Cantidad")
    ax.set_xlabel("Ingrediente")
    
    # Rotar etiquetas si son muchas
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Agregar en Tkinter
    canvas = FigureCanvasTkAgg(fig, master=frame_padre)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)