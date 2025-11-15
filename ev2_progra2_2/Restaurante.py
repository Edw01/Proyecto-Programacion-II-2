from ElementoMenu import CrearMenu
import customtkinter as ctk
from tkinter import ttk, Toplevel, Label, messagebox
from Ingrediente import Ingrediente
from Stock import Stock
import re
from PIL import Image
from CTkMessagebox import CTkMessagebox
from Pedido import Pedido
from BoletaFacade import BoletaFacade
import pandas as pd
from tkinter import filedialog
from Menu_catalog import get_default_menus
from menu_pdf import create_menu_pdf
from ctk_pdf_viewer import CTkPDFViewer
import os
from tkinter.font import nametofont


class AplicacionConPestanas(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gestión de ingredientes y pedidos")
        self.geometry("870x700")
        nametofont("TkHeadingFont").configure(size=14)
        nametofont("TkDefaultFont").configure(size=11)

        self.stock = Stock()
        self.menus_creados = set()

        self.pedido = Pedido()

        self.menus = get_default_menus()

        self.tabview = ctk.CTkTabview(self, command=self.on_tab_change)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)

        self.crear_pestanas()

    def actualizar_treeview_stock(self):
        self.treeview_stock.delete(*self.treeview_stock.get_children())
        for ingrediente in sorted(self.stock.lista_ingredientes, key=lambda item: item.nombre):
            self.treeview_stock.insert("", "end", values=(
                ingrediente.nombre, ingrediente.unidad, ingrediente.cantidad))

    def on_tab_change(self):
        selected_tab = self.tabview.get()
        if selected_tab == "carga de ingredientes":
            print('carga de ingredientes')
        if selected_tab == "Stock":
            self.actualizar_treeview_stock()
        if selected_tab == "Pedido":
            self.actualizar_treeview_stock()
            print('pedido')
        if selected_tab == "Carta restorante":
            self.actualizar_treeview_stock()
            print('Carta restorante')
        if selected_tab == "Boleta":
            self.actualizar_treeview_stock()
            print('Boleta')

    def crear_pestanas(self):
        self.tab3 = self.tabview.add("carga de ingredientes")
        self.tab1 = self.tabview.add("Stock")
        self.tab4 = self.tabview.add("Carta restorante")
        self.tab2 = self.tabview.add("Pedido")
        self.tab5 = self.tabview.add("Boleta")

        self.configurar_pestana_Stock()
        self.configurar_pestana_pedido()
        self.configurar_pestana_csv()
        self._configurar_pestana_crear_menu()
        self._configurar_pestana_ver_boleta()

    def configurar_pestana_csv(self):  # pestaña CSV
        label = ctk.CTkLabel(self.tab3, text="Carga de archivo CSV")
        label.pack(pady=20)
        boton_cargar_csv = ctk.CTkButton(
            self.tab3, text="Cargar CSV", fg_color="#1976D2", text_color="white", command=self.cargar_csv)

        boton_cargar_csv.pack(pady=10)

        self.frame_tabla_csv = ctk.CTkFrame(self.tab3)
        self.frame_tabla_csv.pack(fill="both", expand=True, padx=10, pady=10)
        self.df_csv = None
        self.tabla_csv = None

        self.boton_agregar_stock = ctk.CTkButton(
            self.frame_tabla_csv, text="Agregar al Stock", command=lambda: self.agregar_csv_al_stock())
        self.boton_agregar_stock.pack(side="bottom", pady=10)

    def agregar_csv_al_stock(self):
        if self.df_csv is None:
            CTkMessagebox(
                title="Aviso", message="Primero debes cargar un archivo CSV.", icon="warning")
            return

        for index, row in self.df_csv.iterrows():
            ingrediente = Ingrediente(
                nombre=row["nombre"], unidad=row["unidad"], cantidad=float(row["cantidad"]))
            self.stock.agregar_ingrediente(ingrediente)

        CTkMessagebox(
            title="Éxito", message="Ingredientes del CSV agregados al stock correctamente.")

        self.df_csv = None
        self.actualizar_treeview_stock()

    def cargar_csv(self):
        try:
            # Apertura normal del archivo
            path = filedialog.askopenfile(
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
            self.df_csv = pd.read_csv(path, encoding="UTF-8-SIG")
            # Extracción del BOM
            for columna in self.df_csv.columns:
                new_column_name = re.sub(r"[^0-9a-zA-Z.,-/_ ]", "", columna)
                self.df_csv.rename(
                    columns={columna: new_column_name}, inplace=True)
            # Verificación de estándares del CSV
            if len(self.df_csv.columns) != 3:
                raise Exception
            elif self.df_csv.columns[0].upper() != "nombre".upper():
                raise Exception
            elif self.df_csv.columns[1].upper() != "unidad".upper():
                raise Exception
            elif self.df_csv.columns[2].upper() != "cantidad".upper():
                raise Exception
            # Muestra en tabla
            self.mostrar_dataframe_en_tabla(self.df_csv)
        # Error de archivo
        except UnicodeDecodeError:
            CTkMessagebox(
                title="Error", message="Error al cargar el archivo.", icon="warning")
            return
        except:
            CTkMessagebox(
                title="Error", message="El archivo no cumple con los estándares de ingreso\nde stock.", icon="warning")

    def mostrar_dataframe_en_tabla(self, df):
        if self.tabla_csv:
            self.tabla_csv.destroy()

        self.tabla_csv = ttk.Treeview(
            self.frame_tabla_csv, columns=list(df.columns), show="headings")
        for col in df.columns:
            self.tabla_csv.heading(col, text=col)
            self.tabla_csv.column(col, width=100, anchor="center")

        for _, row in df.iterrows():
            self.tabla_csv.insert("", "end", values=list(row))

        self.tabla_csv.pack(expand=True, fill="both", padx=10, pady=10)

    def actualizar_treeview_pedido(self):
        for item in self.treeview_pedido.get_children():
            self.treeview_pedido.delete(item)

        for menu in self.pedido.menus:
            self.treeview_pedido.insert("", "end", values=(
                menu.nombre, menu.cantidad, f"${menu.precio:.2f}"))

    def _configurar_pestana_crear_menu(self):
        contenedor = ctk.CTkFrame(self.tab4)
        contenedor.pack(expand=True, fill="both", padx=10, pady=10)

        boton_menu = ctk.CTkButton(
            contenedor,
            text="Generar Carta (PDF)",
            command=self.generar_y_mostrar_carta_pdf
        )
        boton_menu.pack(pady=10)

        self.pdf_frame_carta = ctk.CTkFrame(contenedor)
        self.pdf_frame_carta.pack(expand=True, fill="both", padx=10, pady=10)

        self.pdf_viewer_carta = None

    def generar_y_mostrar_carta_pdf(self):
        try:
            pdf_path = "carta.pdf"
            create_menu_pdf(self.menus, pdf_path,
                            titulo_negocio="Restaurante",
                            subtitulo="Carta Primavera 2025",
                            moneda="$")

            if self.pdf_viewer_carta is not None:
                try:
                    self.pdf_viewer_carta.pack_forget()
                    self.pdf_viewer_carta.destroy()
                except Exception:
                    pass
                self.pdf_viewer_carta = None

            abs_pdf = os.path.abspath(pdf_path)
            self.pdf_viewer_carta = CTkPDFViewer(
                self.pdf_frame_carta, file=abs_pdf)
            self.pdf_viewer_carta.pack(expand=True, fill="both")

        except Exception as e:
            CTkMessagebox(
                title="Error", message=f"No se pudo generar/mostrar la carta.\n{e}", icon="warning")

    def _configurar_pestana_ver_boleta(self):
        contenedor = ctk.CTkFrame(self.tab5)
        contenedor.pack(expand=True, fill="both", padx=10, pady=10)

        boton_boleta = ctk.CTkButton(
            contenedor,
            text="Mostrar Boleta (PDF)",
            command=self.mostrar_boleta
        )
        boton_boleta.pack(pady=10)

        self.pdf_frame_boleta = ctk.CTkFrame(contenedor)
        self.pdf_frame_boleta.pack(expand=True, fill="both", padx=10, pady=10)

        self.pdf_viewer_boleta = None

    def mostrar_boleta(self):
        pdf_path = "boleta.pdf"
        
        # Verificar si el archivo PDF existe
        if not os.path.exists(pdf_path):
            CTkMessagebox(
                title="Aviso", message="Primero debes generar la boleta en la pestaña 'Pedido'.", icon="warning")
            return

        # Elimina el "viewer" anterior si existe
        if self.pdf_viewer_boleta is not None:
            try:
                self.pdf_viewer_boleta.pack_forget()
                self.pdf_viewer_boleta.destroy()
            except Exception:
                pass
            self.pdf_viewer_boleta = None
            
        # Crea el nuevo "viewer"
        try:
            abs_pdf = os.path.abspath(pdf_path)
            self.pdf_viewer_boleta = CTkPDFViewer(
                self.pdf_frame_boleta, 
                file=abs_pdf,
                page_width=400, # Ajusta el tamano para que se vea bien en el frame
                page_height=500
            )
            self.pdf_viewer_boleta.pack(expand=True, fill="both")
            
        except Exception as e:
            CTkMessagebox(
                title="Error", message=f"No se pudo mostrar el archivo PDF de la boleta.\n{e}", icon="warning")


    def configurar_pestana_Stock(self):
        frame_stock = self.tabview.tab("Stock")

        frame_formulario = ctk.CTkFrame(frame_stock)
        frame_formulario.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(frame_formulario, text="Nombre:").grid(
            row=0, column=0, padx=5, pady=5)
        self.entry_nombre = ctk.CTkEntry(frame_formulario)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame_formulario, text="Unidad:").grid(
            row=0, column=2, padx=5, pady=5)
        self.combo_unidad = ctk.CTkComboBox(
            frame_formulario, values=["unid", "kg"],state="readonly")
        self.combo_unidad.set("unid")
        self.combo_unidad.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(frame_formulario, text="Cantidad:").grid(
            row=1, column=0, padx=5, pady=5)
        self.entry_cantidad = ctk.CTkEntry(frame_formulario)
        self.entry_cantidad.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkButton(
            frame_formulario,
            text="Ingresar Ingrediente",
            command=self.ingresar_ingrediente
        ).grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky="ew")

        frame_tabla = ctk.CTkFrame(frame_stock)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

        self.treeview_stock = ttk.Treeview(frame_tabla, columns=(
            "Nombre", "Unidad", "Cantidad"), show="headings")
        self.treeview_stock.heading("Nombre", text="Nombre")
        self.treeview_stock.heading("Unidad", text="Unidad")
        self.treeview_stock.heading("Cantidad", text="Cantidad")
        self.treeview_stock.pack(side="top", fill="both", expand=True)

        self.treeview_stock.bind("<Double-1>", self.editar_cantidad_stock)

        ctk.CTkButton(frame_stock, text="Eliminar Ingrediente Seleccionado",
                      command=self.eliminar_ingrediente).pack(side="bottom", pady=10)

        ctk.CTkButton(self.tabview.tab("Stock"), text="Generar Menús Disponibles",
                      command=self.generar_menus).pack(side="bottom", pady=10)

        ctk.CTkButton(self.tabview.tab("Stock"), text="Generar Lista de Compras (Bajo Stock)",
                      command=self.mostrar_lista_compras).pack(side="bottom", pady=10)

    def tarjeta_click(self, event, menu):
        if menu.esta_disponible(self.stock):
            for ingrediente_necesario in menu.ingredientes:
                for ingrediente_stock in self.stock.lista_ingredientes:
                    if ingrediente_necesario.nombre.upper() == ingrediente_stock.nombre.upper():
                        ingrediente_stock.cantidad = str(
                            int(ingrediente_stock.cantidad) - int(ingrediente_necesario.cantidad))

            self.pedido.agregar_menu(menu)
            self.generar_menus()
            self.actualizar_treeview_pedido()
            total = self.pedido.calcular_total()
            self.label_total.configure(text=f"Total: ${total:.2f}")
        else:
            CTkMessagebox(title="Stock Insuficiente",
                          message=f"No hay suficientes ingredientes para preparar el menú '{menu.nombre}'.", icon="warning")

    def cargar_icono_menu(self, ruta_icono):
        imagen = Image.open(ruta_icono)
        icono_menu = ctk.CTkImage(imagen, size=(64, 64))
        return icono_menu

    def generar_menus(self):
        for tarjeta in self.frame_tarjetas.winfo_children():
            tarjeta.destroy()
        listaMenus = get_default_menus()
        columna = 0
        for menu in listaMenus:
            if menu.esta_disponible(self.stock):
                columna += 1
                self.crear_tarjeta(menu, columna)

    def eliminar_menu(self):
        item_seleccionado = self.treeview_pedido.focus()
        if not item_seleccionado:
            CTkMessagebox(
                title="Aviso", message="Selecciona un menú del pedido para eliminar.", icon="warning")
            return

        nombre_menu = self.treeview_pedido.item(item_seleccionado)['values'][0]
        self.pedido.eliminar_menu(nombre_menu)

        menu_a_devolver = next(
            (m for m in self.menus if m.nombre == nombre_menu), None)
        if menu_a_devolver:
            for ing in menu_a_devolver.ingredientes:
                self.stock.agregar_ingrediente(ing)

        total = self.pedido.calcular_total()
        self.label_total.configure(text=f"Total: ${total:.2f}")
        self.actualizar_treeview_stock()
        self.actualizar_treeview_pedido()
        self.on_tab_change()

    def generar_boleta(self):
        # Verifico si hay elementos en el pedido
        if not self.pedido.menus:
            CTkMessagebox(
                title="Aviso", message="El pedido está vacío. Agrega menús antes de generar la boleta.", icon="warning")
            return

        # Crear una instancia del Facade (que ya esta importado)
        boleta_facade = BoletaFacade(self.pedido)

        # Generar el PDF y obtener la ruta (BoletaFacade.generar_boleta() es el que se encarga de esto)
        try:
            # La funcion generar_boleta en BoletaFacade ahora va a retornar la ruta del archivo
            ruta_pdf = boleta_facade.generar_boleta()
            
            # Limpiar el pedido despues de generar la boleta
            self.pedido.menus = []
            
            # Actualizar la interfaz de usuario
            self.actualizar_treeview_pedido()
            self.label_total.configure(text="Total: $0.00")
            
            CTkMessagebox(
                title="Exito", message=(os.path.basename(ruta_pdf)), icon="check")
            
            # Opcionalmente, cambiar a la pestana de boleta y mostrarla asi automaticamente
            self.tabview.set("Boleta")
            self.mostrar_boleta()

        except Exception as e:
            CTkMessagebox(
                title="Error", message=f"Ocurrio un error al generar la boleta.\n{e}", icon="cancel")


    def configurar_pestana_pedido(self):
        frame_superior = ctk.CTkFrame(self.tab2)
        frame_superior.pack(side="top", fill="both",
                            expand=True, padx=10, pady=10)

        frame_intermedio = ctk.CTkFrame(self.tab2)
        frame_intermedio.pack(side="top", fill="x", padx=10, pady=5)

        self.frame_tarjetas = ctk.CTkScrollableFrame(
            frame_superior, label_text="Menús Disponibles")
        self.frame_tarjetas.pack(expand=True, fill="both", padx=10, pady=10)

        self.boton_eliminar_menu = ctk.CTkButton(
            frame_intermedio, text="Eliminar Menú", command=self.eliminar_menu)
        self.boton_eliminar_menu.pack(side="right", padx=10)

        self.label_total = ctk.CTkLabel(
            frame_intermedio, text="Total: $0.00", anchor="e", font=("Helvetica", 12, "bold"))
        self.label_total.pack(side="right", padx=10)

        frame_inferior = ctk.CTkFrame(self.tab2)
        frame_inferior.pack(side="bottom", fill="both",
                            expand=True, padx=10, pady=10)

        self.treeview_pedido = ttk.Treeview(frame_inferior, columns=(
            "Nombre", "Cantidad", "Precio Unitario"), show="headings")
        self.treeview_pedido.heading("Nombre", text="Nombre del Menú")
        self.treeview_pedido.heading("Cantidad", text="Cantidad")
        self.treeview_pedido.heading("Precio Unitario", text="Precio Unitario")
        self.treeview_pedido.pack(expand=True, fill="both", padx=10, pady=10)

        self.boton_generar_boleta = ctk.CTkButton(
            frame_inferior, text="Generar Boleta", command=self.generar_boleta) # Boletilla--------------------
        self.boton_generar_boleta.pack(side="bottom", pady=10)

    def crear_tarjeta(self, menu, columna):
        fila = 0
        # columna = num_tarjetas

        tarjeta = ctk.CTkFrame(
            self.frame_tarjetas,
            corner_radius=10,
            border_width=1,
            border_color="#4CAF50",
            width=64,
            height=140,
            fg_color="gray",
        )
        tarjeta.grid(row=fila, column=columna, padx=15, pady=15, sticky="nsew")

        tarjeta.bind(
            "<Button-1>", lambda event: self.tarjeta_click(event, menu))
        tarjeta.bind("<Enter>", lambda event: tarjeta.configure(
            border_color="#FF0000"))
        tarjeta.bind("<Leave>", lambda event: tarjeta.configure(
            border_color="#4CAF50"))

        if getattr(menu, "icono_path", None):
            try:
                icono = self.cargar_icono_menu(menu.icono_path)
                imagen_label = ctk.CTkLabel(
                    tarjeta, image=icono, width=64, height=64, text="", bg_color="transparent"
                )
                imagen_label.image = icono
                imagen_label.pack(anchor="center", pady=5, padx=10)
                imagen_label.bind(
                    "<Button-1>", lambda event: self.tarjeta_click(event, menu))
            except Exception as e:
                print(f"No se pudo cargar la imagen '{menu.icono_path}': {e}")

        texto_label = ctk.CTkLabel(
            tarjeta,
            text=f"{menu.nombre}",
            text_color="black",
            font=("Helvetica", 12, "bold"),
            bg_color="transparent",
        )
        texto_label.pack(anchor="center", pady=1)
        texto_label.bind(
            "<Button-1>", lambda event: self.tarjeta_click(event, menu))
        return tarjeta

    def validar_nombre(self, nombre):
        if re.match(r"^[a-zA-Z\s]+$", nombre):
            return True
        else:
            CTkMessagebox(title="Error de Validación",
                          message="El nombre debe contener solo letras y espacios.", icon="warning")
            return False

    def validar_cantidad(self, cantidad):
        # No debe ser un numero vacio
        if not cantidad.strip():
            CTkMessagebox(title="Error de Cantidad", message="El campo de cantidad no puede estar vacío.", icon="cancel")
            return False

        # Debe ser un número válido
        try:
            cantidad_num = float(cantidad)
        except ValueError:
            CTkMessagebox(title="Error de Cantidad", message="La cantidad debe ser un número válido (ej: 10 o 5.5).", icon="cancel")
            return False

        # Debe ser un numero mayor a 0
        if cantidad_num <= 0:
            CTkMessagebox(title="Error de Cantidad", message="La cantidad debe ser un número mayor que cero.", icon="cancel")
            return False

        return True

    def ingresar_ingrediente(self):
        nombre = self.entry_nombre.get()
        unidad = self.combo_unidad.get()
        cantidad = self.entry_cantidad.get()

        if not self.validar_nombre(nombre) or not self.validar_cantidad(cantidad):
            return

        ingrediente_a_agregar = Ingrediente(nombre, unidad, float(cantidad))

        self.stock.agregar_ingrediente(ingrediente_a_agregar)

        self.entry_nombre.delete(0, 'end')
        self.entry_cantidad.delete(0, 'end')

        self.actualizar_treeview_stock()

    def eliminar_ingrediente(self):
        item_seleccionado = self.treeview_stock.focus()
        if not item_seleccionado:
            CTkMessagebox(
                title="Aviso", message="Debes seleccionar un ingrediente de la tabla.", icon="warning")
            return

        detalles_item = self.treeview_stock.item(item_seleccionado)
        nombre_a_eliminar = detalles_item['values'][0]

        self.stock.eliminar_ingrediente(nombre_a_eliminar)
        self.actualizar_treeview_stock()

    def editar_cantidad_stock(self, event):
        # 1. Identifica la fila en la que se hizo doble clic
        item_seleccionado = self.treeview_stock.focus()
        if not item_seleccionado:
            return

        # 2. Obtiene los detalles del ingrediente de esa fila
        detalles_item = self.treeview_stock.item(item_seleccionado)
        nombre_ingrediente = detalles_item['values'][0]
        cantidad_actual = detalles_item['values'][2]

        # 3. Abre una ventana emergente para pedir la nueva cantidad
        dialogo = ctk.CTkInputDialog(
            text=f"Ingrese la nueva cantidad para '{nombre_ingrediente}':",
            title="Actualizar Stock"
        )

        nueva_cantidad_str = dialogo.get_input()

        # 4. Si el usuario ingresó un valor y no canceló
        if nueva_cantidad_str:
            try:
                nueva_cantidad = float(nueva_cantidad_str)
                if nueva_cantidad < 0:  # No permitir cantidades negativas
                    raise ValueError

                # 5. Llama a la función de la lógica del Stock
                self.stock.actualizar_stock(nombre_ingrediente, nueva_cantidad)

                # 6. Refresca la tabla para mostrar el cambio
                self.actualizar_treeview_stock()

            except (ValueError, TypeError):
                CTkMessagebox(
                    title="Error", message="Por favor, ingrese un número válido y positivo.", icon="cancel")

    def mostrar_lista_compras(self):
        # 1. Llama a la nueva función de la lógica del Stock
        ingredientes_bajos = self.stock.obtener_elementos_menu(
            umbral=5)  # Puedes cambiar el umbral

        # 2. Prepara el mensaje para el usuario
        if not ingredientes_bajos:
            mensaje = "¡Excelente! No hay ingredientes con bajo stock."
        else:
            mensaje = "Se recomienda comprar los siguientes ingredientes:\n\n"
            # Formatea la lista para que sea fácil de leer
            for ingrediente in ingredientes_bajos:
                mensaje += f"- {ingrediente.nombre} (Quedan: {ingrediente.cantidad})\n"

        # 3. Muestra el resultado en una ventana de información
        CTkMessagebox(title="Lista de Compras", message=mensaje, icon="info")


if __name__ == "__main__":
    import customtkinter as ctk
    from tkinter import ttk

    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    ctk.set_widget_scaling(1.0)
    ctk.set_window_scaling(1.0)

    app = AplicacionConPestanas()

    try:
        style = ttk.Style(app)
        style.theme_use("clam")
    except Exception:
        pass

    app.mainloop()
