import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from sqlalchemy.orm import joinedload
from models import Pedido, Menu, MenuIngrediente
from collections import Counter

class Graficos:
    
    @staticmethod
    def obtener_datos(db, tipo_grafico, periodo=None):
        """
        Extrae y procesa los datos de la BD usando Carga Ansiosa (joinedload).
        Retorna: (etiquetas, valores, mensaje_error)
        """
        etiquetas = []
        valores = []
        
        try:
            # --- CONSULTA MAESTRA ---
            # Traemos Pedidos + Menús + Receta + Ingredientes (Todo junto)
            # Esto soluciona que los gráficos no detecten cambios.
            pedidos = db.query(Pedido).options(
                joinedload(Pedido.menus)
                .joinedload(Menu.ingredientes_receta)
                .joinedload(MenuIngrediente.ingrediente)
            ).all()

            if not pedidos:
                return [], [], "No hay pedidos registrados para graficar."

            # --- LÓGICA SEGÚN TIPO ---
            
            if tipo_grafico == "Ventas por Fecha":
                data_agrupada = {}
                
                for p in pedidos:
                    # Si no tiene fecha, usamos hoy (seguridad)
                    if not p.fecha: continue
                        
                    key = ""
                    if periodo == "Diario":
                        key = p.fecha.strftime("%Y-%m-%d")
                    elif periodo == "Mensual":
                        key = p.fecha.strftime("%Y-%m")
                    elif periodo == "Anual":
                        key = p.fecha.strftime("%Y")
                    else:
                        key = p.fecha.strftime("%Y-%m-%d")
                    
                    data_agrupada[key] = data_agrupada.get(key, 0) + 1

                # Ordenar cronológicamente
                for k in sorted(data_agrupada.keys()):
                    etiquetas.append(k)
                    valores.append(data_agrupada[k])

            elif tipo_grafico == "Distribución Menús":
                conteo = Counter()
                hay_datos = False
                
                for p in pedidos:
                    # p.menus ahora SÍ tiene datos gracias a joinedload
                    for m in p.menus:
                        conteo[m.nombre] += 1
                        hay_datos = True
                
                if not hay_datos:
                    return [], [], "Hay pedidos, pero no tienen menús asociados."

                # Top 10 más vendidos
                for nombre, cant in conteo.most_common(10):
                    etiquetas.append(nombre)
                    valores.append(cant)

            elif tipo_grafico == "Uso de Ingredientes":
                conteo = Counter()
                hay_datos = False
                
                for p in pedidos:
                    for m in p.menus:
                        # Accedemos a la tabla intermedia (Association Object)
                        for item_receta in m.ingredientes_receta:
                            # item_receta.ingrediente es el objeto Ingrediente real
                            nombre_ing = item_receta.ingrediente.nombre
                            
                            # Opción A: Contar frecuencia de uso (1 pedido = 1 voto)
                            conteo[nombre_ing] += 1
                            
                            # Opción B (Más avanzada): Sumar cantidad real usada
                            # conteo[nombre_ing] += item_receta.cantidad_requerida
                            
                            hay_datos = True
                
                if not hay_datos:
                    return [], [], "Los menús vendidos no tienen ingredientes definidos."

                # Top 10 ingredientes más usados
                for nombre, cant in conteo.most_common(10):
                    etiquetas.append(nombre)
                    valores.append(cant)

            return etiquetas, valores, None

        except Exception as e:
            print(f"Error en gráficos: {e}")
            return [], [], f"Error al procesar datos: {str(e)}"

    @staticmethod
    def crear_figura(etiquetas, valores, tipo_grafico):
        """
        Genera la Figura de Matplotlib.
        """
        # Ajustamos el tamaño para que se vea bien en la app
        fig = Figure(figsize=(6, 4.5), dpi=100)
        ax = fig.add_subplot(111)

        if not etiquetas:
            return fig 

        if tipo_grafico == "Distribución Menús":
            # Gráfico de Pastel
            ax.pie(valores, labels=etiquetas, autopct='%1.1f%%', startangle=90)
            ax.set_title("Menús Más Vendidos")
        
        else:
            # Gráfico de Barras
            colores = 'skyblue' if tipo_grafico == "Ventas por Fecha" else 'lightgreen'
            barras = ax.bar(etiquetas, valores, color=colores)
            
            ax.set_title(tipo_grafico)
            ax.set_ylabel("Frecuencia / Cantidad")
            
            # Rotar etiquetas para que no se superpongan
            ax.tick_params(axis='x', rotation=45, labelsize=9)
            
            # Etiquetas de valor sobre las barras
            for bar in barras:
                height = bar.get_height()
                ax.annotate(f'{int(height)}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3), 
                            textcoords="offset points",
                            ha='center', va='bottom')
        
        fig.tight_layout() 
        return fig