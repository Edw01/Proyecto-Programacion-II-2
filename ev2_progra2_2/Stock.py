from Ingrediente import Ingrediente


class Stock:
    def __init__(self):
        self.lista_ingredientes = []

    def agregar_ingrediente(self, nuevo_ingrediente: Ingrediente):
        # Normaliza el nombre del nuevo ingrediente para una comparación que no distinga mayúsculas ni espacios.
        nombre_normalizado_nuevo = nuevo_ingrediente.nombre.replace(" ", "").lower()

        # Itera sobre la lista de ingredientes existentes para buscar duplicados.
        for ingrediente_existente in self.lista_ingredientes:
            # Normaliza el nombre del ingrediente existente para asegurar una comparación justa.
            nombre_normalizado_existente = ingrediente_existente.nombre.replace(" ", "").lower()

            # Si se encuentra una coincidencia, actualiza la cantidad del ingrediente existente.
            if nombre_normalizado_existente == nombre_normalizado_nuevo:
                ingrediente_existente.cantidad = float(ingrediente_existente.cantidad)
                return

        # Si el bucle termina sin encontrar una coincidencia, agrega el ítem como un ingrediente nuevo.
        nuevo_ingrediente.cantidad = float(nuevo_ingrediente.cantidad)
        self.lista_ingredientes.append(nuevo_ingrediente)

    def eliminar_ingrediente(self, nombre_ingrediente: str):
        self.lista_ingredientes = [
            ing for ing in self.lista_ingredientes if ing.nombre.lower() != nombre_ingrediente.lower()
        ]

    def verificar_stock(self, menu):
        suficiente_stock = True
    
        # Si la lista de inventario está completamente vacía, es imposible preparar algo.
        if not self.lista_ingredientes:
            suficiente_stock = False

        # Itera sobre cada ingrediente que el menú necesita.
        for ingrediente_necesario in menu.ingredientes:
            # Busca el ingrediente necesario dentro de la lista del inventario.
            for ingrediente_stock in self.lista_ingredientes:
                # Compara los nombres para encontrar una coincidencia.
                if ingrediente_necesario.nombre == ingrediente_stock.nombre:
                    # Si se encuentra, verifica si la cantidad en stock es menor a la requerida.
                    if int(ingrediente_stock.cantidad) < int(ingrediente_necesario.cantidad):
                        # Si un solo ingrediente no es suficiente, retorna False inmediatamente.
                        return False
        
            # Si el stock está vacío, rompe el bucle principal para optimizar.
            if not suficiente_stock:
                break
        # Si el bucle termina sin haber retornado False, significa que todos los ingredientes están disponibles.
        return True

    def actualizar_stock(self, nombre_ingrediente: str, nueva_cantidad: float):
        """
        Busca un ingrediente por su nombre y actualiza su cantidad.
        Devuelve True si lo encontró y actualizó, False en caso contrario.
        """
        for ingrediente in self.lista_ingredientes:
            # Busca el ingrediente ignorando mayúsculas/minúsculas
            if ingrediente.nombre.lower() == nombre_ingrediente.lower():
                ingrediente.cantidad = nueva_cantidad
                return True  
        return False 

    def obtener_elementos_menu(self, umbral: int = 5):
        """
        Revisa el inventario y devuelve una lista de los ingredientes
        cuya cantidad es igual o menor al umbral especificado.

        Args:
            umbral (int): La cantidad mínima que activa la alerta de bajo stock.

        Returns:
            list: Una lista de objetos Ingrediente que necesitan ser repuestos.
        """
        lista_para_comprar = []
        for ingrediente in self.lista_ingredientes:
            # Aplica la lógica solo para ingredientes contados por unidad
            if ingrediente.unidad == "unid" and int(ingrediente.cantidad) <= umbral:
                lista_para_comprar.append(ingrediente)
        return lista_para_comprar
