import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog  # AGREGADO filedialog
from database import get_session, engine, Base, verificar_conexion
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sqlalchemy.orm import joinedload
from crud.cliente_crud import ClienteCRUD
from crud.pedido_crud import PedidoCRUD
from crud.ingrediente_crud import IngredienteCRUD
from crud.menu_crud import MenuCRUD
from graficos import Graficos
from models import Pedido, MenuIngrediente, Menu
from fpdf import FPDF
from datetime import datetime
from tkcalendar import DateEntry


# Configuración inicial
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
Base.metadata.create_all(bind=engine)


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        if not verificar_conexion():
            messagebox.showerror(
                "Error Crítico", "No se pudo conectar a la Base de Datos.\nVerifique que el archivo .db no esté bloqueado.")
            self.destroy()  # Cierra la app
            return

        self.title("Gestión de Restaurante - Evaluación 3")
        self.geometry("950x700")

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(pady=10, padx=10, fill="both", expand=True)

        self.tab_clientes = self.tabview.add("Clientes")
        self.tab_ingredientes = self.tabview.add("Stock / Ingredientes")
        self.tab_menu = self.tabview.add("Menu")
        self.tab_compra = self.tabview.add("Panel de Compra")
        self.tab_pedidos = self.tabview.add("Pedidos")
        self.tab_graficos = self.tabview.add("Gráficos")

        self.crear_interfaz_clientes()
        self.crear_interfaz_ingredientes()
        self.crear_interfaz_menu()
        self.crear_panel_compra()
        self.crear_interfaz_pedidos()
        self.crear_interfaz_graficos()

    # --------------------------------------------------------------------------------------
    # PESTAÑA CLIENTES
    # --------------------------------------------------------------------------------------

    def crear_interfaz_clientes(self):

        # Creación de la interfaz de Clientes

        frame = self.tab_clientes
        frame_form = ctk.CTkFrame(frame)
        frame_form.pack(pady=10, padx=10, fill="x")

        self.entry_nombre_cli = ctk.CTkEntry(
            frame_form, placeholder_text="Nombre Completo")
        self.entry_nombre_cli.pack(side="left", padx=5, expand=True, fill="x")
        self.entry_email_cli = ctk.CTkEntry(
            frame_form, placeholder_text="Email (ID)")
        self.entry_email_cli.pack(side="left", padx=5, expand=True, fill="x")
        self.entry_edad_cli = ctk.CTkEntry(
            frame_form, placeholder_text="Edad", width=80)
        self.entry_edad_cli.pack(side="left", padx=5)

        frame_botones = ctk.CTkFrame(frame, fg_color="transparent")
        frame_botones.pack(pady=5)
        ctk.CTkButton(frame_botones, text="Guardar",
                      command=self.guardar_cliente).pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Refrescar",
                      command=self.cargar_clientes).pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Eliminar", command=self.eliminar_cliente,
                      fg_color="red").pack(side="left", padx=5)

        columns = ("nombre", "email", "edad")
        self.tree_clientes = ttk.Treeview(
            frame, columns=columns, show="headings")
        self.tree_clientes.heading("nombre", text="Nombre")
        self.tree_clientes.heading("email", text="Email")
        self.tree_clientes.heading("edad", text="Edad")
        self.tree_clientes.pack(expand=True, fill="both", padx=10, pady=10)

        # Carga de Clientes en el Treeview del listado
        self.cargar_clientes()

    def guardar_cliente(self):

        # Recolección de datos
        nombre = self.entry_nombre_cli.get()
        email = self.entry_email_cli.get()
        edad_str = self.entry_edad_cli.get()

        # Validación previa del valor de edad
        try:
            edad = int(edad_str)
        except ValueError:
            messagebox.showerror("Error", "Edad inválida")
            return
        
        # CRUD: Creación de Cliente y actualización automática de listado
        db = next(get_session())
        if ClienteCRUD.crear_cliente(db, nombre, email, edad):
            messagebox.showinfo("Éxito", "Cliente guardado")
            self.cargar_clientes()
        else:
            messagebox.showerror("Error", "No se pudo guardar")
        db.close()

    def cargar_clientes(self):
        
        tree = getattr(self, 'tree_clientes', None) or getattr(self, 'treeview_clientes', None)
        
        if not tree:
            print("Error: No se encontró la tabla de clientes.")
            return

        # Limpieza de Treeview previo
        for item in tree.get_children():
            tree.delete(item)
        
        # CRUD: Lectura de Clientes
        db = next(get_session())
        clientes = ClienteCRUD.leer_clientes(db)
        db.close()

        # Llenado del Treeview con registros de Cliente
        for c in clientes:
            # Ajusta los valores según las columnas que tengas
            tree.insert("", "end", values=(c.nombre, c.email, c.edad))


    def eliminar_cliente(self):

        # Validación de la selección de un cliente en Treeview
        selected = self.tree_clientes.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione un cliente de la lista.")
            return
        
        # Obtención de la PK del cliente
        email = self.tree_clientes.item(selected[0])['values'][1]
        
        # CRUD: Eliminación de cliente con mensaje preventivo, se captura un valor del resultado de la operación
        if messagebox.askyesno("Confirmar", f"¿Eliminar cliente {email}?"):
            db = next(get_session())
            resultado = ClienteCRUD.borrar_cliente(db, email)
            db.close()
            
            # Manejo e información del resultado de la eliminación
            if resultado == "OK":
                messagebox.showinfo("Éxito", "Cliente eliminado correctamente.")
                self.cargar_clientes()
            elif resultado == "Tiene Pedidos":
                messagebox.showerror("Acción Denegada", 
                                     "No se puede eliminar este cliente porque tiene PEDIDOS asociados.\n"
                                     "Borre los pedidos primero si realmente desea eliminarlo.")
            else:
                messagebox.showerror("Error", "No se pudo eliminar el cliente.")




    # --------------------------------------------------------------------------------------
    # PESTAÑA INGREDIENTES
    # --------------------------------------------------------------------------------------

    def crear_interfaz_ingredientes(self):

        # Creación de la interfaz de Ingredientes

        frame = self.tab_ingredientes
        frame_form = ctk.CTkFrame(frame)
        frame_form.pack(pady=10, padx=10, fill="x")

        self.entry_nombre_ing = ctk.CTkEntry(
            frame_form, placeholder_text="Nombre")
        self.entry_nombre_ing.pack(side="left", padx=5, expand=True, fill="x")
        self.combo_unidad = ctk.CTkComboBox(
            frame_form, values=["unid", "kg", "lt"], state="readonly", width=80)
        self.combo_unidad.pack(side="left", padx=5)
        self.entry_cantidad_ing = ctk.CTkEntry(
            frame_form, placeholder_text="Cant", width=80)
        self.entry_cantidad_ing.pack(side="left", padx=5)

        frame_botones = ctk.CTkFrame(frame, fg_color="transparent")
        frame_botones.pack(pady=5)

        ctk.CTkButton(frame_botones, text="Guardar",
                      command=self.guardar_ingrediente).pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Cargar CSV", command=self.importar_csv,
                      fg_color="green").pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Bajo Stock (<5)",
                      command=self.filtrar_bajo_stock, fg_color="orange").pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Ver Todos (Refrescar)",
                       command=self.cargar_ingredientes, fg_color="#3B8ED0").pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Eliminar", command=self.eliminar_ingrediente,
                      fg_color="red").pack(side="left", padx=5)

        columns = ("id", "nombre", "unidad", "cantidad")
        self.tree_ingredientes = ttk.Treeview(
            frame, columns=columns, show="headings")
        self.tree_ingredientes.heading("id", text="ID")
        self.tree_ingredientes.heading("nombre", text="Nombre")
        self.tree_ingredientes.heading("unidad", text="Unidad")
        self.tree_ingredientes.heading("cantidad", text="Cantidad")
        self.tree_ingredientes.pack(expand=True, fill="both", padx=10, pady=10)

        # Carga de Ingredientes en el Treeview del listado
        self.cargar_ingredientes()

    def importar_csv(self):
        # Apertura normal del archivo
        archivo = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")])
        # CRUD: Creación masiva de Ingrediente con procesado de filas de CSV
        if archivo:
            db = next(get_session())
            mensaje = IngredienteCRUD.cargar_masivamente_desde_csv(db, archivo)
            db.close()
            messagebox.showinfo("Carga CSV", mensaje)
            self.cargar_ingredientes()

    def guardar_ingrediente(self):
        try:
            cant = float(self.entry_cantidad_ing.get())
            nom = self.entry_nombre_ing.get()
            uni = self.combo_unidad.get()
            db = next(get_session())
            if IngredienteCRUD.crear_ingrediente(db, nom, uni, cant):
                messagebox.showinfo("Éxito", "Guardado")
                self.cargar_ingredientes()
            else:
                messagebox.showerror("Error", "Datos inválidos o duplicado")
            db.close()
        except ValueError:
            messagebox.showerror("Error", "Cantidad numérica requerida")

    def cargar_ingredientes(self):
        for item in self.tree_ingredientes.get_children():
            self.tree_ingredientes.delete(item)
        db = next(get_session())
        for ing in IngredienteCRUD.leer_ingredientes(db):
            self.tree_ingredientes.insert("", "end", values=(
                ing.id, ing.nombre, ing.unidad, ing.cantidad))
        db.close()

    def filtrar_bajo_stock(self):
        for item in self.tree_ingredientes.get_children():
            self.tree_ingredientes.delete(item)
        db = next(get_session())
        for ing in IngredienteCRUD.obtener_ingredientes_bajo_stock(db):
            self.tree_ingredientes.insert("", "end", values=(
                ing.id, ing.nombre, ing.unidad, ing.cantidad))
        db.close()

    def eliminar_ingrediente(self):
        sel = self.tree_ingredientes.selection()
        if sel:
            id_ing = self.tree_ingredientes.item(sel[0])['values'][0]
            db = next(get_session())
            IngredienteCRUD.borrar_ingrediente(db, id_ing)
            db.close()
            self.cargar_ingredientes()

    # PESTAÑA MENUS

    def crear_interfaz_menu(self):
        frame = self.tab_menu

        # --- Formulario de Creación ---
        frame_form = ctk.CTkFrame(frame)
        frame_form.pack(pady=10, padx=10, fill="x")

        self.entry_nombre_menu = ctk.CTkEntry(
            frame_form, placeholder_text="Nombre del Menú")
        self.entry_nombre_menu.pack(side="left", padx=5, expand=True, fill="x")

        self.entry_desc_menu = ctk.CTkEntry(
            frame_form, placeholder_text="Descripción")
        self.entry_desc_menu.pack(side="left", padx=5, expand=True, fill="x")
        

        self.entry_precio_menu = ctk.CTkEntry(frame_form, placeholder_text="Precio ($)", width=80)
        self.entry_precio_menu.pack(side="left", padx=5)
        # Campo para ingresar IDs
        self.entry_receta = ctk.CTkEntry(
            frame_form, placeholder_text="Receta (ID:Cant, ID:Cant)", width=200)
        self.entry_receta.pack(side="left", padx=5)

        # Botones
        frame_botones = ctk.CTkFrame(frame, fg_color="transparent")
        frame_botones.pack(pady=5)

        ctk.CTkButton(frame_botones, text="Crear Menú",
                      command=self.guardar_menu).pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Refrescar",
                      command=self.cargar_menus).pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Eliminar", command=self.eliminar_menu,
                      fg_color="red").pack(side="left", padx=5)

        # Agregamos la columna "receta"
        columns = ("id", "nombre", "descripcion", "receta", "precio")

        self.tree_menus = ttk.Treeview(frame, columns=columns, show="headings")

        self.tree_menus.heading("id", text="ID")
        self.tree_menus.column("id", width=30)  # Hacemos el ID más pequeño

        self.tree_menus.heading("nombre", text="Nombre")
        self.tree_menus.column("nombre", width=150)

        self.tree_menus.heading("descripcion", text="Descripción")
        self.tree_menus.column("descripcion", width=200)

        # Receta (Ingredientes y cantidad)
        self.tree_menus.heading("receta", text="Ingredientes (Receta)")
        self.tree_menus.column("receta", width=330)  # Le damos harto espacio

        # Precio
        self.tree_menus.heading("precio", text="Precio")
        self.tree_menus.column("precio", width=120)

        self.tree_menus.pack(expand=True, fill="both", padx=10, pady=10)

        self.cargar_menus()

    def cargar_menus(self):
        for item in self.tree_menus.get_children():
            self.tree_menus.delete(item)

        db = next(get_session())
        menus = MenuCRUD.leer_menus(db)

        for m in menus:
            # Usamos una comprensión de lista (similar a map) para formatear el texto.
            # Accedemos a 'm.ingredientes_receta' que definimos en models.py

            detalle_receta = ", ".join([
                f"{item.ingrediente.nombre} ({item.cantidad_requerida} {item.ingrediente.unidad})"
                for item in m.ingredientes_receta
            ])

            # Si no tiene ingredientes (por seguridad), mostramos vacío
            if not detalle_receta:
                detalle_receta = "Sin ingredientes definidos"

            # Insertamos en la tabla incluyendo la nueva columna
            self.tree_menus.insert("", "end", values=(
                m.id, m.nombre, m.descripcion, detalle_receta, f"${m.precio: .2f}"))
        db.close()

    def guardar_menu(self):
        nombre = self.entry_nombre_menu.get()
        desc = self.entry_desc_menu.get()
        receta_str = self.entry_receta.get() # String tipo "1:10, 3:5"
        precio_str = self.entry_precio_menu.get()  

        if not nombre or not receta_str or not precio_str:
            messagebox.showwarning("Datos", "Todos los campos son obligatorios.")
            return

        # Validar que precio sea número
        try:
            precio = int(precio_str)
            if precio < 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número entero positivo.")
            return

        # Procesar el string de receta para convertirlo en la lista que pide tu CRUD
        # Tu CRUD espera: [(id_ingrediente, cantidad), ...]
        lista_ingredientes = []
        try:
            # Lógica rápida para parsear el texto "1:10, 2:5"
            items = receta_str.split(',')
            for item in items:
                datos = item.split(':')
                id_ing = int(datos[0].strip())
                cant = float(datos[1].strip())
                lista_ingredientes.append((id_ing, cant))
        except Exception:
            messagebox.showerror(
                "Error Formato", "Formato de receta incorrecto.\nUse: ID:CANTIDAD, ID:CANTIDAD\nEjemplo: 1:100, 2:5")
            return

        db = next(get_session())
        # Llamamos a tu función avanzada con LAMBDA/MAP/REDUCE
        nuevo = MenuCRUD.crear_menu(db, nombre, desc, lista_ingredientes, precio)
        db.close()

        if nuevo:
            messagebox.showinfo("Éxito", "Menú creado correctamente.")
            self.cargar_menus()
            # Limpiar campos
            self.entry_nombre_menu.delete(0, 'end')
            self.entry_desc_menu.delete(0, 'end')
            self.entry_receta.delete(0, 'end')
        else:
            messagebox.showerror(
                "Error", "No se pudo crear.\nVerifique:\n1. IDs de ingredientes existan.\n2. Stock suficiente.\n3. Cantidades positivas.")

    def eliminar_menu(self):
        sel = self.tree_menus.selection()
        if sel:
            id_menu = self.tree_menus.item(sel[0])['values'][0]
            db = next(get_session())
            MenuCRUD.borrar_menu(db, id_menu)
            db.close()
            self.cargar_menus()


    # PESTAÑA COMPRA 

    def generar_totales_pedido(self, pedido):
        """Calcula subtotal, IVA y total de un pedido."""
        subtotal = sum(menu.precio for menu in pedido.menus)
        iva = subtotal * 0.19
        total = subtotal + iva
        return subtotal, iva, total

    def crear_boleta_pdf(self, pedido, archivo_salida=None):
        """Crea la boleta PDF a partir de un objeto Pedido."""
        subtotal, iva, total = self.generar_totales_pedido(pedido)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # --- Encabezado ---
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Boleta Restaurante", ln=True, align='L')
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, "Razón Social del Negocio", ln=True, align='L')
        pdf.cell(0, 10, "RUT: 12345678-9", ln=True, align='L')
        pdf.cell(0, 10, "Dirección: Calle Falsa 123", ln=True, align='L')
        pdf.cell(0, 10, "Teléfono: +56 9 1234 5678", ln=True, align='L')
        pdf.cell(
            0, 10, f"Cliente: {pedido.cliente.nombre} ({pedido.cliente.email})", ln=True, align='L')
        pdf.cell(
            0, 10, f"Fecha: {pedido.fecha.strftime('%d/%m/%Y %H:%M:%S')}", ln=True, align='R')
        pdf.ln(10)

        # --- Tabla de Menús ---
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(70, 10, "Nombre Menú", border=1)
        pdf.cell(35, 10, "Precio Unitario", border=1)
        pdf.ln()

        pdf.set_font("Arial", size=12)
        for menu in pedido.menus:
            pdf.cell(70, 10, menu.nombre, border=1)
            pdf.cell(35, 10, f"${menu.precio:.2f}", border=1)
            pdf.ln()

        # --- Totales ---
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(105, 10, "Subtotal:", 0, 0, 'R')
        pdf.cell(35, 10, f"${subtotal:.2f}", ln=True, align='R')

        pdf.cell(105, 10, "IVA (19%):", 0, 0, 'R')
        pdf.cell(35, 10, f"${iva:.2f}", ln=True, align='R')

        pdf.cell(105, 10, "Total:", 0, 0, 'R')
        pdf.cell(35, 10, f"${total:.2f}", ln=True, align='R')

        # --- Pie ---
        pdf.set_font("Arial", 'I', 10)
        pdf.ln(10)
        pdf.multi_cell(
            0, 10, "Gracias por su compra. Para cualquier consulta, llámenos al +56 9 777 5678.", 0, 'C')
        pdf.multi_cell(
            0, 10, "Los productos adquiridos no tienen garantía.", 0, 'C')

        # Nombre del archivo PDF
        if archivo_salida is None:
            archivo_salida = f"boleta_{pedido.id}.pdf"

        pdf.output(archivo_salida)
        return archivo_salida

    def crear_interfaz_compra(self):
        frame = self.tab_compra
        frame_form = ctk.CTkFrame(frame)
        frame_form.pack(pady=10, padx=10, fill="x")

        # INGRESO DE DATOS DEL PEDIDO

        # Selección del cliente
        db = next(get_session())
        self.clientes_db = ClienteCRUD.leer_clientes(db)
        cliente_nombres = [c.email for c in self.clientes_db]
        self.combo_clientes = ctk.CTkOptionMenu(
            frame_form,
            values=cliente_nombres
        )
        self.combo_clientes.pack(side="left", padx=5, expand=True, fill="x")

        # Descripción del pedido
        self.entry_desc_ped = ctk.CTkEntry(
            frame_form, placeholder_text="Descripción")
        self.entry_desc_ped.pack(side="left", padx=5, expand=True, fill="x")

        # Fecha del pedido
        self.dateentry_fecha = DateEntry(frame_form, date_pattern='yyyy-mm-dd')
        self.dateentry_fecha.pack(side="left", padx=5, expand=True, fill="x")

        # ctk.CTkButton(frame_form, text="Total Ventas (Reduce)",
        #         command=self.ver_total_ventas, fg_color="green").pack(side="left", padx=5)

        # --- FRAME PARA MENÚS ---
        frame_menus = ctk.CTkFrame(frame)
        frame_menus.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(frame_menus, text="Seleccionar menú:").pack(anchor="w")
        self.combo_menus = ctk.CTkOptionMenu(frame_menus, values=["---"])
        db = next(get_session())
        self.menus_db = MenuCRUD.leer_menus(db)
        menu_nombres = [menu.nombre for menu in self.menus_db]
        if menu_nombres:
            self.combo_menus.configure(values=menu_nombres)
        else:
            self.combo_menus.configure(values=["No hay menús"])

        self.combo_menus.pack(fill="x", padx=5, pady=5)

        # Botón: Agregar menú al pedido
        ctk.CTkButton(
            frame_menus, text="Agregar menú",
            command=self.agregar_menu_seleccionado
        ).pack(pady=5)

        # Botón: Registrar Pedido en BD
        ctk.CTkButton(
            frame_form,
            text="Crear Pedido",
            fg_color="blue",
            command=self.crear_pedido  # llamará al método que crearemos
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_form,
            text="Refrescar",
            command=self.actualizar_listados,
            fg_color="green"
        ).pack(side="left", padx=5)

        columns_sel = ("menu", "precio")
        self.tree_menus_seleccionados = ttk.Treeview(
            frame, columns=columns_sel, show="headings"
        )
        self.tree_menus_seleccionados.heading("menu", text="Menú")
        self.tree_menus_seleccionados.heading("precio", text="Precio")
        self.tree_menus_seleccionados.pack(
            expand=True, fill="both", padx=10, pady=10)

        self.label_total = ctk.CTkLabel(
            frame, text="TOTAL: $0.00", font=ctk.CTkFont(size=14, weight="bold"))
        self.label_total.pack(pady=5)

    def agregar_menu_seleccionado(self):
        seleccionado = self.combo_menus.get()
        if not seleccionado or seleccionado in ["---", "No hay menús"]:
            return  # no hacer nada si no se ha seleccionado un menú válido

        # Buscar el objeto Menu real en la lista cargada desde la BD
        menu_obj = next(
            (m for m in self.menus_db if m.nombre == seleccionado), None)
        if not menu_obj:
            return

        # Crear la lista temporal si no existe
        if not hasattr(self, "menus_seleccionados"):
            self.menus_seleccionados = []

        print(menu_obj.id)
        print("Hola")

        # Evitar duplicados
        if any(m.id == menu_obj.id for m in self.menus_seleccionados):
            return
        else:
            self.menus_seleccionados.append(menu_obj)
            # Insertar nombre y precio en TreeView
            self.tree_menus_seleccionados.insert(
                "", "end", values=(menu_obj.nombre, f"${menu_obj.precio:.2f}")
            )

        # Calcular y mostrar total
        total = sum(m.precio for m in self.menus_seleccionados)
        self.label_total.configure(text=f"TOTAL: ${total:.2f}")

    def crear_pedido(self):

        cliente_email = self.combo_clientes.get().strip()
        descripcion = self.entry_desc_ped.get().strip()
        fecha = self.dateentry_fecha.get_date()

        if not cliente_email or not descripcion:
            print("Debe seleccionar un cliente y escribir una descripción")
            return

        if not hasattr(self, "menus_seleccionados") or not self.menus_seleccionados:
            print("Debe agregar al menos un menú al pedido")
            return

        # Crear el pedido

        db = next(get_session())

        pedido = PedidoCRUD.crear_pedido(db, cliente_email, descripcion, fecha)
        if not pedido:
            print("No se pudo crear el pedido")
            return

        # Asociar menús
        for menu in self.menus_seleccionados:
            # Recuperamos el objeto Menu en la sesión actual
            menu_db = db.get(type(menu), menu.id)
            pedido.menus.append(menu_db)

        # Guardar cambios
        if PedidoCRUD._try_commit(db):
            print(f"Pedido creado con éxito: ID {pedido.id}")
        else:
            print("Error al guardar los menús en el pedido")

            # 2. Generar PDF
        archivo_pdf = self.crear_boleta_pdf(pedido)
        print(f"PDF generado: {archivo_pdf}")

        # Limpiar interfaz
        self.menus_seleccionados.clear()
        for item in self.tree_menus_seleccionados.get_children():
            self.tree_menus_seleccionados.delete(item)

    def actualizar_listados(self):
        """Actualiza los combos de clientes y menús desde la BD."""
        db = next(get_session())

        # --- Actualizar clientes ---
        self.clientes_db = ClienteCRUD.leer_clientes(db)
        cliente_nombres = [c.email for c in self.clientes_db]
        if cliente_nombres:
            self.combo_clientes.configure(values=cliente_nombres)
        else:
            self.combo_clientes.configure(values=["No hay clientes"])
        self.combo_clientes.set("")  # opcional: limpiar selección actual

        # --- Actualizar menús ---
        self.menus_db = MenuCRUD.leer_menus(db)
        menu_nombres = [m.nombre for m in self.menus_db]
        if menu_nombres:
            self.combo_menus.configure(values=menu_nombres)
        else:
            self.combo_menus.configure(values=["No hay menús"])
        self.combo_menus.set("---")  # opcional: limpiar selección actual

    def ver_total_ventas(self):
        db = next(get_session())
        tot = PedidoCRUD.calcular_total_ventas(db)
        db.close()
        messagebox.showinfo("Total", f"Ventas: ${tot:,.0f}")

    # PESTAÑA PEDIDOS (MANIPULACIÓN DE PEDIDOS [RUD])

    def crear_interfaz_pedidos(self):
        frame = self.tab_pedidos
        
        # --- FILTROS DE BÚSQUEDA ---
        frame_filtros = ctk.CTkFrame(frame)
        frame_filtros.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(frame_filtros, text="Filtrar por Email Cliente:").pack(side="left", padx=5)
        self.entry_cliente_email_ped = ctk.CTkEntry(frame_filtros, placeholder_text="email@cliente.com")
        self.entry_cliente_email_ped.pack(side="left", padx=5, expand=True, fill="x")
        
        ctk.CTkButton(frame_filtros, text="Buscar", command=self.cargar_pedidos).pack(side="left", padx=5)

        # --- BOTONES DE ACCIÓN ---
        frame_botones = ctk.CTkFrame(frame, fg_color="transparent")
        frame_botones.pack(pady=5)
        
        ctk.CTkButton(frame_botones, text="Actualizar Lista", command=self.cargar_pedidos).pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Anular Pedido (Devolver Stock)", command=self.eliminar_pedido, fg_color="red").pack(side="left", padx=5)
        
        # --- TABLA DE HISTORIAL ---
        columns = ("id", "cliente", "descripcion", "fecha")
        self.tree_pedidos = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        self.tree_pedidos.heading("id", text="ID")
        self.tree_pedidos.column("id", width=50)
        
        self.tree_pedidos.heading("cliente", text="Cliente")
        self.tree_pedidos.column("cliente", width=200)
        
        self.tree_pedidos.heading("descripcion", text="Detalle Compra")
        self.tree_pedidos.column("descripcion", width=300)
        
        self.tree_pedidos.heading("fecha", text="Fecha")
        self.tree_pedidos.column("fecha", width=120)
        
        self.tree_pedidos.pack(expand=True, fill="both", padx=10, pady=10)

        self.cargar_pedidos()

    def actualizar_combo_menus(self):
        db = next(get_session())
        menus = MenuCRUD.leer_menus(db)
        db.close()
        # Guardamos los nombres para el combo
        nombres = [f"{m.id}: {m.nombre} (${m.precio})" for m in menus]
        self.combo_menus.configure(values=nombres)
        if nombres: self.combo_menus.set(nombres[0])

    def agregar_al_carrito(self):
        seleccion = self.combo_menus.get()
        if not seleccion: return

        # Extraer ID del string "1: Completo ($1500)"
        id_menu = int(seleccion.split(":")[0])
        
        # Buscar el objeto menu en BD para tenerlo listo
        db = next(get_session())
        menu = db.query(Menu).get(id_menu) # Traemos el objeto simple
        db.close() # Cerramos, pero guardamos el dato básico (ID, Nombre, Precio)

        if menu:
            self.lista_carrito.append(menu) # Guardamos en memoria
            
            # Actualizar visualización
            self.text_carrito.configure(state="normal")
            self.text_carrito.insert("end", f"• {menu.nombre} - ${menu.precio}\n")
            self.text_carrito.configure(state="disabled")

    def confirmar_compra(self):
        email = self.entry_cliente_ped.get()
        if not email or not self.lista_carrito:
            messagebox.showwarning("Faltan Datos", "Ingrese email del cliente y agregue productos al carrito.")
            return

        # Necesitamos re-consultar los menús dentro de la sesión de transacción
        # para que SQLAlchemy los reconozca y pueda descontar ingredientes
        db = next(get_session())
        
        # Obtenemos los IDs del carrito
        ids_menus = [m.id for m in self.lista_carrito]
        
        # Cargamos los objetos REALES con sus ingredientes listos
        # Usamos 'in_' para traerlos todos de una vez
        menus_para_venta = db.query(Menu).options(
            joinedload(Menu.ingredientes_receta).joinedload("ingrediente")
        ).filter(Menu.id.in_(ids_menus)).all()
        
        # Llamamos al CRUD Transaccional
        descripcion_automatica = f"Venta de {len(self.lista_carrito)} items"
        resultado = PedidoCRUD.crear_pedido_con_stock(db, email, descripcion_automatica, menus_para_venta)
        
        db.close()

        if resultado == "OK":
            messagebox.showinfo("Venta Exitosa", "Pedido creado y stock descontado correctamente.")
            self.lista_carrito = [] # Vaciar carrito
            self.text_carrito.configure(state="normal")
            self.text_carrito.delete("1.0", "end")
            self.text_carrito.configure(state="disabled")
            self.cargar_pedidos()
        else:
            messagebox.showerror("Error en Venta", f"No se pudo procesar:\n{resultado}")

    def eliminar_pedido(self):
        sel = self.tree_pedidos.selection()
        if not sel: return
        id_ped = self.tree_pedidos.item(sel[0])['values'][0]

        if messagebox.askyesno("Devolución", "Al eliminar el pedido se devolverá el stock.\n¿Confirmar?"):
            db = next(get_session())
            exito = PedidoCRUD.borrar_pedido_y_restaurar_stock(db, id_ped)
            db.close()

            if exito:
                messagebox.showinfo("Éxito", "Pedido anulado y stock restaurado.")
                self.cargar_pedidos()
            else:
                messagebox.showerror("Error", "No se pudo anular el pedido.")

    def cargar_pedidos(self, *args):
        # 1. Limpiar la tabla actual
        for item in self.tree_pedidos.get_children():
            self.tree_pedidos.delete(item)

        # 2. Obtener texto de búsqueda (Filtro)
        # Usamos try/except por seguridad si el campo aún no se ha creado
        try:
            texto_busqueda = self.entry_cliente_email_ped.get().strip().lower()
        except AttributeError:
            texto_busqueda = ""

        # 3. Traer TODOS los pedidos de la BD
        db = next(get_session())
        todos_pedidos = PedidoCRUD.leer_pedidos(db)
        db.close()

        # 4. APLICAR FILTRO (Programación Funcional)
        if texto_busqueda:
            # Usamos FILTER + LAMBDA para dejar solo los que coincidan con el email
            # "in" permite búsquedas parciales (ej: "juan" encuentra "juan@gmail.com")
            pedidos_a_mostrar = list(filter(
                lambda p: texto_busqueda in p.cliente_email.lower(), 
                todos_pedidos
            ))
        else:
            # Si no escribió nada, mostramos todo
            pedidos_a_mostrar = todos_pedidos

        # 5. Llenar la tabla con los resultados (Filtrados o Todos)
        for p in pedidos_a_mostrar:
            # Formatear fecha de manera segura
            fecha_str = ""
            if p.fecha:
                # Validamos si es string o datetime
                if isinstance(p.fecha, str):
                    fecha_str = p.fecha
                else:
                    fecha_str = p.fecha.strftime("%Y-%m-%d %H:%M")
            
            # Insertamos en la tabla (ID, Cliente, Descripción, Fecha)
            self.tree_pedidos.insert("", "end", values=(p.id, p.cliente_email, p.descripcion, fecha_str))
            
        # Opcional: Mostrar mensaje si buscó algo y no encontró nada
        if texto_busqueda and not pedidos_a_mostrar:
            pass

    # PESTAÑA GRAFICOS

    def crear_interfaz_graficos(self):
        frame = self.tab_graficos

        # --- Panel de Control ---
        frame_ctrl = ctk.CTkFrame(frame)
        frame_ctrl.pack(pady=10, padx=10, fill="x")

        # Selector de Tipo
        ctk.CTkLabel(frame_ctrl, text="Tipo:").pack(side="left", padx=5)
        self.combo_tipo = ctk.CTkComboBox(
            frame_ctrl,
            values=["Ventas por Fecha",
                    "Distribución Menús", "Uso de Ingredientes"],
            command=self.actualizar_combo_periodo,  # Evento al cambiar
            state="readonly",
            width=180
        )
        self.combo_tipo.set("Ventas por Fecha")
        self.combo_tipo.pack(side="left", padx=5)

        # Selector de Periodo (Solo visible para Fechas)
        self.combo_periodo = ctk.CTkComboBox(
            frame_ctrl,
            values=["Diario", "Mensual", "Anual"],
            state="readonly",
            width=100
        )
        self.combo_periodo.set("Diario")
        self.combo_periodo.pack(side="left", padx=5)

        # Botón Generar
        ctk.CTkButton(frame_ctrl, text="Generar Gráfico",
                      command=self.generar_grafico).pack(side="left", padx=20)

        # --- Área de Dibujo ---
        self.frame_canvas = ctk.CTkFrame(frame)
        self.frame_canvas.pack(expand=True, fill="both", padx=10, pady=10)
        self.canvas_actual = None

    def actualizar_combo_periodo(self, seleccion):
        """Habilita o deshabilita el periodo según el tipo de gráfico"""
        if seleccion == "Ventas por Fecha":
            self.combo_periodo.configure(state="normal")
        else:
            self.combo_periodo.configure(state="disabled")

    def generar_grafico(self):
        tipo = self.combo_tipo.get()
        periodo = self.combo_periodo.get()

        # 1. Obtener sesión y Datos
        db = next(get_session())
        etiquetas, valores, error = Graficos.obtener_datos(db, tipo, periodo)
        db.close()

        # 2. Validaciones de la Rúbrica
        if error:
            # Limpiar gráfico anterior
            if self.canvas_actual:
                self.canvas_actual.get_tk_widget().destroy()
                self.canvas_actual = None

            # "Mostrar mensaje si no existen registros"
            messagebox.showinfo("Información", error)
            return

        # 3. Generar Figura
        figura = Graficos.crear_figura(etiquetas, valores, tipo)

        # 4. Incrustar en Tkinter
        if self.canvas_actual:
            self.canvas_actual.get_tk_widget().destroy()

        self.canvas_actual = FigureCanvasTkAgg(
            figura, master=self.frame_canvas)
        self.canvas_actual.draw()
        self.canvas_actual.get_tk_widget().pack(expand=True, fill="both")

    # --------------------------------------------------------------------------------------
    # PESTAÑA DE COMPRA
    # --------------------------------------------------------------------------------------

    def crear_panel_compra(self):
        frame = self.tab_compra
        self.lista_carrito = [] # Lista temporal de objetos Menu

        # --- SELECCIÓN DE CLIENTE ---
        frame_cli = ctk.CTkFrame(frame)
        frame_cli.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(frame_cli, text="1. Seleccionar Cliente:").pack(side="left", padx=5)
        self.combo_clientes_compra = ctk.CTkComboBox(frame_cli, width=250, state="readonly")
        self.combo_clientes_compra.pack(side="left", padx=5)
        
        # Botón para recargar la lista de clientes si creaste uno nuevo
        ctk.CTkButton(frame_cli, text="🔄", width=30, command=self.cargar_combo_clientes).pack(side="left", padx=5)

        # --- SELECCIÓN DE PRODUCTOS ---
        frame_prod = ctk.CTkFrame(frame)
        frame_prod.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(frame_prod, text="2. Agregar Producto:").pack(side="left", padx=5)
        self.combo_menus_compra = ctk.CTkComboBox(frame_prod, width=250, state="readonly")
        self.combo_menus_compra.pack(side="left", padx=5)

        ctk.CTkButton(frame_prod, text="🔄", width=30, command=self.cargar_combo_menus).pack(side="left", padx=5)

        ctk.CTkButton(frame_prod, text="Agregar al Carrito", command=self.agregar_al_carrito).pack(side="left", padx=10)

        # --- RESUMEN (CARRITO) ---
        ctk.CTkLabel(frame, text="3. Detalle del Pedido:").pack(pady=(10,0))
        self.text_boleta_preview = ctk.CTkTextbox(frame, height=150)
        self.text_boleta_preview.pack(fill="x", padx=10, pady=5)
        self.text_boleta_preview.configure(state="disabled")

        # --- NUEVO: SELECCIÓN DE FECHA ---
        frame_fecha = ctk.CTkFrame(frame)
        frame_fecha.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(frame_fecha, text="Fecha del Pedido:").pack(side="left", padx=5)
        
        # Widget de Calendario
        self.cal_fecha_compra = DateEntry(frame_fecha, width=12, background='darkblue',
                                          foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.cal_fecha_compra.pack(side="left", padx=5)

        # --- ACCIONES ---
        frame_actions = ctk.CTkFrame(frame, fg_color="transparent")
        frame_actions.pack(pady=10)

        ctk.CTkButton(frame_actions, text="Limpiar Carrito", fg_color="red", command=self.limpiar_carrito).pack(side="left", padx=10)
        
        # EL BOTÓN PRINCIPAL
        ctk.CTkButton(frame_actions, text="GENERAR BOLETA Y GUARDAR", fg_color="green", height=40, command=self.procesar_compra).pack(side="left", padx=10)

        # Cargar datos iniciales
        self.cargar_combo_clientes()
        self.cargar_combo_menus()

    def cargar_combo_clientes(self):
        db = next(get_session())
        clientes = ClienteCRUD.leer_clientes(db)
        db.close()
        # Guardamos el email que es la PK
        lista = [c.email for c in clientes]
        self.combo_clientes_compra.configure(values=lista)
        if lista: self.combo_clientes_compra.set(lista[0])

    def cargar_combo_menus(self):
        db = next(get_session())
        menus = MenuCRUD.leer_menus(db)
        db.close()
        # Guardamos "ID: Nombre ($Precio)"
        lista = [f"{m.id}: {m.nombre} (${m.precio})" for m in menus]
        self.combo_menus_compra.configure(values=lista)
        if lista: self.combo_menus_compra.set(lista[0])

    def agregar_al_carrito(self):
        seleccion = self.combo_menus_compra.get()
        if not seleccion: return

        # Extraer ID del string "1: Completo ($1500)"
        try:
            id_menu = int(seleccion.split(":")[0])
        except ValueError:
            return

        if any(m.id == id_menu for m in self.lista_carrito):
            return

        db = next(get_session())
        
        # Usamos MenuIngrediente.ingrediente (Clase) en vez de "ingrediente" (String)
        menu = db.query(Menu).options(
            joinedload(Menu.ingredientes_receta).joinedload(MenuIngrediente.ingrediente)
        ).get(id_menu)
        
        db.close()

        if menu:
            self.lista_carrito.append(menu)
            self.actualizar_vista_carrito()

    def actualizar_vista_carrito(self):
        self.text_boleta_preview.configure(state="normal")
        self.text_boleta_preview.delete("1.0", "end")
        
        total = 0
        for m in self.lista_carrito:
            self.text_boleta_preview.insert("end", f"• {m.nombre} \t\t ${m.precio}\n")
            total += m.precio
            
        self.text_boleta_preview.insert("end", f"\nTOTAL ESTIMADO: ${total}")
        self.text_boleta_preview.configure(state="disabled")

    def limpiar_carrito(self):
        self.lista_carrito = []
        self.actualizar_vista_carrito()

    def procesar_compra(self):
        # 1. Obtener Cliente
        email_cliente = self.combo_clientes_compra.get()
        
        # 2. OBTENER FECHA DEL CALENDARIO
        fecha_obj = self.cal_fecha_compra.get_date() # Retorna objeto date (YYYY-MM-DD)
        
        # Validaciones básicas
        if not email_cliente:
            messagebox.showwarning("Faltan Datos", "Debe seleccionar un cliente.")
            return
        if not self.lista_carrito:
            messagebox.showwarning("Carrito Vacío", "Agregue productos antes de generar la boleta.")
            return

        # 3. Llamar al CRUD
        db = next(get_session())
        
        ids_menus = [m.id for m in self.lista_carrito]
        
        # Usamos la clase MenuIngrediente para evitar el error de strings
        menus_frescos = db.query(Menu).options(
            joinedload(Menu.ingredientes_receta).joinedload(MenuIngrediente.ingrediente)
        ).filter(Menu.id.in_(ids_menus)).all()

        # PASAMOS LA FECHA AL CRUD
        exito, resultado = PedidoCRUD.procesar_compra(db, email_cliente, menus_frescos, fecha_seleccionada=fecha_obj)
        db.close()

        if exito:
            messagebox.showinfo("Compra Exitosa", resultado)
            self.limpiar_carrito()
        else:
            messagebox.showerror("Error en Compra", resultado)


if __name__ == "__main__":
    app = App()
    app.mainloop()
