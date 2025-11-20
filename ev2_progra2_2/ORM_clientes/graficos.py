import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from sqlalchemy import func
from models import Pedido, Menu, Ingrediente
from collections import Counter

class Graficos:
    
    @staticmethod
    def obtener_datos(db, tipo_grafico, periodo=None):
        """
        Extrae y procesa los datos de la BD.
        Retorna: (etiquetas, valores, mensaje_error)
        """
        etiquetas = []
        valores = []
        
        try:
            if tipo_grafico == "Ventas por Fecha":
                # Obtenemos todos los pedidos
                pedidos = db.query(Pedido).all()
                if not pedidos:
                    return [], [], "No hay pedidos registrados."

                # Agrupamos usando Python (Más fácil de controlar periodos que SQL directo)
                data_agrupada = {}
                
                for p in pedidos:
                    fecha = p.fecha
                    key = ""
                    if periodo == "Diario":
                        key = fecha.strftime("%Y-%m-%d")
                    elif periodo == "Mensual":
                        key = fecha.strftime("%Y-%m")
                    elif periodo == "Anual":
                        key = fecha.strftime("%Y")
                    else:
                        key = fecha.strftime("%Y-%m-%d")
                    
                    data_agrupada[key] = data_agrupada.get(key, 0) + 1

                # Ordenar por fecha
                for k in sorted(data_agrupada.keys()):
                    etiquetas.append(k)
                    valores.append(data_agrupada[k])

            elif tipo_grafico == "Distribución Menús":
                # Contar frecuencia de menús en pedidos
                pedidos = db.query(Pedido).all()
                conteo = Counter()
                
                for p in pedidos:
                    # Asumiendo que p.menu es la relación
                    for m in p.menu:
                        conteo[m.nombre] += 1
                
                if not conteo:
                    return [], [], "No hay menús vendidos aún."

                # Top 10
                for nombre, cant in conteo.most_common(10):
                    etiquetas.append(nombre)
                    valores.append(cant)

            elif tipo_grafico == "Uso de Ingredientes":
                # Contar ingredientes basado en menús vendidos
                pedidos = db.query(Pedido).all()
                conteo = Counter()
                
                for p in pedidos:
                    for m in p.menu:
                        for ing in m.ingrediente:
                            # Sumamos 1 vez por uso (o ing.cantidad si tuvieramos el dato exacto)
                            conteo[ing.nombre] += 1
                
                if not conteo:
                    return [], [], "No se han utilizado ingredientes aún."

                # Top 10
                for nombre, cant in conteo.most_common(10):
                    etiquetas.append(nombre)
                    valores.append(cant)

            return etiquetas, valores, None

        except Exception as e:
            return [], [], f"Error al procesar datos: {str(e)}"

    @staticmethod
    def crear_figura(etiquetas, valores, tipo_grafico):
        """
        Genera la Figura de Matplotlib lista para incrustar.
        """
        # Crear figura (Tamaño 5x4 pulgadas, 100 dpi)
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)

        if not etiquetas:
            return fig # Retorna figura vacía si no hay datos

        if tipo_grafico == "Distribución Menús":
            # Gráfico de Torta
            ax.pie(valores, labels=etiquetas, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
            ax.set_title("Menús Más Vendidos")
        
        else:
            # Gráfico de Barras
            colores = 'skyblue' if tipo_grafico == "Ventas por Fecha" else 'lightgreen'
            barras = ax.bar(etiquetas, valores, color=colores)
            
            ax.set_title(tipo_grafico)
            ax.set_ylabel("Cantidad")
            
            # Rotar etiquetas en eje X si son muchas
            ax.tick_params(axis='x', rotation=45, labelsize=8)
            
            # Poner números sobre las barras
            for bar in barras:
                height = bar.get_height()
                ax.annotate(f'{int(height)}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3), 
                            textcoords="offset points",
                            ha='center', va='bottom')
        
        fig.tight_layout() # Ajustar márgenes
        return fig