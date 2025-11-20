import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog # AGREGADO filedialog
from database import get_session, engine, Base
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from crud.cliente_crud import ClienteCRUD
from crud.pedido_crud import PedidoCRUD
from crud.ingrediente_crud import IngredienteCRUD
from crud.menu_crud import MenuCRUD
from graficos import Graficos

# Configuración inicial
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
Base.metadata.create_all(bind=engine)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestión de Restaurante - Evaluación 3")
        self.geometry("950x700")

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(pady=10, padx=10, fill="both", expand=True)

        self.tab_clientes = self.tabview.add("Clientes")
        self.tab_ingredientes = self.tabview.add("Stock / Ingredientes")
        self.tab_menu = self.tabview.add("Menu")
        self.tab_pedidos = self.tabview.add("Pedidos")
        self.tab_graficos = self.tabview.add("Gráficos")

        self.crear_interfaz_clientes()
        self.crear_interfaz_ingredientes()
        self.crear_interfaz_menu()
        self.crear_interfaz_pedidos()
        self.crear_interfaz_graficos()

    # --- PESTAÑA CLIENTES ---
    def crear_interfaz_clientes(self):
        frame = self.tab_clientes
        frame_form = ctk.CTkFrame(frame)
        frame_form.pack(pady=10, padx=10, fill="x")

        self.entry_nombre_cli = ctk.CTkEntry(frame_form, placeholder_text="Nombre Completo")
        self.entry_nombre_cli.pack(side="left", padx=5, expand=True, fill="x")
        self.entry_email_cli = ctk.CTkEntry(frame_form, placeholder_text="Email (ID)")
        self.entry_email_cli.pack(side="left", padx=5, expand=True, fill="x")
        self.entry_edad_cli = ctk.CTkEntry(frame_form, placeholder_text="Edad", width=80)
        self.entry_edad_cli.pack(side="left", padx=5)

        frame_botones = ctk.CTkFrame(frame, fg_color="transparent")
        frame_botones.pack(pady=5)
        ctk.CTkButton(frame_botones, text="Guardar", command=self.guardar_cliente).pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Refrescar", command=self.cargar_clientes).pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Eliminar", command=self.eliminar_cliente, fg_color="red").pack(side="left", padx=5)

        columns = ("nombre", "email", "edad")
        self.tree_clientes = ttk.Treeview(frame, columns=columns, show="headings")
        self.tree_clientes.heading("nombre", text="Nombre")
        self.tree_clientes.heading("email", text="Email")
        self.tree_clientes.heading("edad", text="Edad")
        self.tree_clientes.pack(expand=True, fill="both", padx=10, pady=10)
        self.cargar_clientes()

    def guardar_cliente(self):
        nombre = self.entry_nombre_cli.get()
        email = self.entry_email_cli.get()
        edad_str = self.entry_edad_cli.get()
        try:
            edad = int(edad_str)
        except ValueError:
            messagebox.showerror("Error", "Edad inválida")
            return
        
        db = next(get_session())
        if ClienteCRUD.crear_cliente(db, nombre, email, edad):
            messagebox.showinfo("Éxito", "Cliente guardado")
            self.cargar_clientes()
        else:
            messagebox.showerror("Error", "No se pudo guardar")
        db.close()

    def cargar_clientes(self):
        for item in self.tree_clientes.get_children(): self.tree_clientes.delete(item)
        db = next(get_session())
        for c in ClienteCRUD.leer_clientes(db):
            self.tree_clientes.insert("", "end", values=(c.nombre, c.email, c.edad))
        db.close()

    def eliminar_cliente(self):
        sel = self.tree_clientes.selection()
        if sel:
            email = self.tree_clientes.item(sel[0])['values'][1]
            db = next(get_session())
            ClienteCRUD.borrar_cliente(db, email)
            db.close()
            self.cargar_clientes()

    # --- PESTAÑA INGREDIENTES ---
    def crear_interfaz_ingredientes(self):
        frame = self.tab_ingredientes
        frame_form = ctk.CTkFrame(frame)
        frame_form.pack(pady=10, padx=10, fill="x")

        self.entry_nombre_ing = ctk.CTkEntry(frame_form, placeholder_text="Nombre")
        self.entry_nombre_ing.pack(side="left", padx=5, expand=True, fill="x")
        self.combo_unidad = ctk.CTkComboBox(frame_form, values=["unid", "kg", "lt"], state="readonly", width=80)
        self.combo_unidad.pack(side="left", padx=5)
        self.entry_cantidad_ing = ctk.CTkEntry(frame_form, placeholder_text="Cant", width=80)
        self.entry_cantidad_ing.pack(side="left", padx=5)

        frame_botones = ctk.CTkFrame(frame, fg_color="transparent")
        frame_botones.pack(pady=5)

        ctk.CTkButton(frame_botones, text="Guardar", command=self.guardar_ingrediente).pack(side="left", padx=5)
        # BOTÓN CSV
        ctk.CTkButton(frame_botones, text="Cargar CSV", command=self.importar_csv, fg_color="green").pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Bajo Stock (<5)", command=self.filtrar_bajo_stock, fg_color="orange").pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Eliminar", command=self.eliminar_ingrediente, fg_color="red").pack(side="left", padx=5)

        columns = ("id", "nombre", "unidad", "cantidad")
        self.tree_ingredientes = ttk.Treeview(frame, columns=columns, show="headings")
        self.tree_ingredientes.heading("id", text="ID")
        self.tree_ingredientes.heading("nombre", text="Nombre")
        self.tree_ingredientes.heading("unidad", text="Unidad")
        self.tree_ingredientes.heading("cantidad", text="Cantidad")
        self.tree_ingredientes.pack(expand=True, fill="both", padx=10, pady=10)
        self.cargar_ingredientes()

    def importar_csv(self):
        archivo = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
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
        for item in self.tree_ingredientes.get_children(): self.tree_ingredientes.delete(item)
        db = next(get_session())
        for ing in IngredienteCRUD.leer_ingredientes(db):
            self.tree_ingredientes.insert("", "end", values=(ing.id, ing.nombre, ing.unidad, ing.cantidad))
        db.close()

    def filtrar_bajo_stock(self):
        for item in self.tree_ingredientes.get_children(): self.tree_ingredientes.delete(item)
        db = next(get_session())
        for ing in IngredienteCRUD.obtener_ingredientes_bajo_stock(db):
            self.tree_ingredientes.insert("", "end", values=(ing.id, ing.nombre, ing.unidad, ing.cantidad))
        db.close()

    def eliminar_ingrediente(self):
        sel = self.tree_ingredientes.selection()
        if sel:
            id_ing = self.tree_ingredientes.item(sel[0])['values'][0]
            db = next(get_session())
            IngredienteCRUD.borrar_ingrediente(db, id_ing)
            db.close()
            self.cargar_ingredientes()

    # --- PESTAÑA PEDIDOS ---
    def crear_interfaz_pedidos(self):
        frame = self.tab_pedidos
        frame_form = ctk.CTkFrame(frame)
        frame_form.pack(pady=10, padx=10, fill="x")

        self.entry_cliente_email_ped = ctk.CTkEntry(frame_form, placeholder_text="Email Cliente")
        self.entry_cliente_email_ped.pack(side="left", padx=5, expand=True, fill="x")
        self.entry_desc_ped = ctk.CTkEntry(frame_form, placeholder_text="Descripción")
        self.entry_desc_ped.pack(side="left", padx=5, expand=True, fill="x")

        ctk.CTkButton(frame_form, text="Crear Pedido", command=self.crear_pedido).pack(side="left", padx=5)
        ctk.CTkButton(frame_form, text="Total Ventas (Reduce)", command=self.ver_total_ventas, fg_color="green").pack(side="left", padx=5)

        columns = ("id", "cliente", "descripcion")
        self.tree_pedidos = ttk.Treeview(frame, columns=columns, show="headings")
        self.tree_pedidos.heading("id", text="ID")
        self.tree_pedidos.heading("cliente", text="Cliente")
        self.tree_pedidos.heading("descripcion", text="Descripción")
        self.tree_pedidos.pack(expand=True, fill="both", padx=10, pady=10)
        self.cargar_pedidos()

    def crear_pedido(self):
        db = next(get_session())
        if PedidoCRUD.crear_pedido(db, self.entry_cliente_email_ped.get(), self.entry_desc_ped.get()):
            messagebox.showinfo("Éxito", "Pedido creado")
            self.cargar_pedidos()
        else:
            messagebox.showerror("Error", "Fallo al crear")
        db.close()

    def cargar_pedidos(self):
        for item in self.tree_pedidos.get_children(): self.tree_pedidos.delete(item)
        db = next(get_session())
        for p in PedidoCRUD.leer_pedidos(db):
            self.tree_pedidos.insert("", "end", values=(p.id, p.cliente_email, p.descripcion))
        db.close()

    def ver_total_ventas(self):
        db = next(get_session())
        tot = PedidoCRUD.calcular_total_ventas(db)
        db.close()
        messagebox.showinfo("Total", f"Ventas: ${tot:,.0f}")

    # --- PESTAÑA MENUS ---
    def crear_interfaz_menu(self):
        frame = self.tab_menu
        
        # --- Formulario de Creación ---
        frame_form = ctk.CTkFrame(frame)
        frame_form.pack(pady=10, padx=10, fill="x")

        self.entry_nombre_menu = ctk.CTkEntry(frame_form, placeholder_text="Nombre del Menú")
        self.entry_nombre_menu.pack(side="left", padx=5, expand=True, fill="x")
        
        self.entry_desc_menu = ctk.CTkEntry(frame_form, placeholder_text="Descripción")
        self.entry_desc_menu.pack(side="left", padx=5, expand=True, fill="x")

        # Campo para ingresar IDs
        self.entry_receta = ctk.CTkEntry(frame_form, placeholder_text="Receta (ID:Cant, ID:Cant)", width=200)
        self.entry_receta.pack(side="left", padx=5)

        # Botones
        frame_botones = ctk.CTkFrame(frame, fg_color="transparent")
        frame_botones.pack(pady=5)
        
        ctk.CTkButton(frame_botones, text="Crear Menú", command=self.guardar_menu).pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Refrescar", command=self.cargar_menus).pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Eliminar", command=self.eliminar_menu, fg_color="red").pack(side="left", padx=5)

        # --- TABLA (TREEVIEW) ACTUALIZADA ---
        # Agregamos la columna "receta"
        columns = ("id", "nombre", "descripcion", "receta") 
        
        self.tree_menus = ttk.Treeview(frame, columns=columns, show="headings")
        
        self.tree_menus.heading("id", text="ID")
        self.tree_menus.column("id", width=30) # Hacemos el ID más pequeño
        
        self.tree_menus.heading("nombre", text="Nombre")
        self.tree_menus.column("nombre", width=150)
        
        self.tree_menus.heading("descripcion", text="Descripción")
        self.tree_menus.column("descripcion", width=200)
        
        # Configuración de la nueva columna
        self.tree_menus.heading("receta", text="Ingredientes (Receta)")
        self.tree_menus.column("receta", width=400) # Le damos harto espacio
        
        self.tree_menus.pack(expand=True, fill="both", padx=10, pady=10)

        self.cargar_menus()

    def guardar_menu(self):
        nombre = self.entry_nombre_menu.get()
        desc = self.entry_desc_menu.get()
        receta_str = self.entry_receta.get() # String tipo "1:10, 3:5"

        if not nombre or not receta_str:
            messagebox.showwarning("Datos", "Nombre y Receta son obligatorios.")
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
            messagebox.showerror("Error Formato", "Formato de receta incorrecto.\nUse: ID:CANTIDAD, ID:CANTIDAD\nEjemplo: 1:100, 2:5")
            return

        db = next(get_session())
        # Llamamos a tu función avanzada con LAMBDA/MAP/REDUCE
        nuevo = MenuCRUD.crear_menu(db, nombre, desc, lista_ingredientes)
        db.close()

        if nuevo:
            messagebox.showinfo("Éxito", "Menú creado correctamente.")
            self.cargar_menus()
            # Limpiar campos
            self.entry_nombre_menu.delete(0, 'end')
            self.entry_desc_menu.delete(0, 'end')
            self.entry_receta.delete(0, 'end')
        else:
            messagebox.showerror("Error", "No se pudo crear.\nVerifique:\n1. IDs de ingredientes existan.\n2. Stock suficiente.\n3. Cantidades positivas.")

    def cargar_menus(self):
        for item in self.tree_menus.get_children():
            self.tree_menus.delete(item)
        
        db = next(get_session())
        menus = MenuCRUD.leer_menus(db)
        db.close()

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
            self.tree_menus.insert("", "end", values=(m.id, m.nombre, m.descripcion, detalle_receta))

    def eliminar_menu(self):
        sel = self.tree_menus.selection()
        if sel:
            id_menu = self.tree_menus.item(sel[0])['values'][0]
            db = next(get_session())
            MenuCRUD.borrar_menu(db, id_menu)
            db.close()
            self.cargar_menus()

    # --- PESTAÑA GRAFICOS ---
    def crear_interfaz_graficos(self):
        frame = self.tab_graficos
        
        # --- Panel de Control ---
        frame_ctrl = ctk.CTkFrame(frame)
        frame_ctrl.pack(pady=10, padx=10, fill="x")

        # Selector de Tipo
        ctk.CTkLabel(frame_ctrl, text="Tipo:").pack(side="left", padx=5)
        self.combo_tipo = ctk.CTkComboBox(
            frame_ctrl, 
            values=["Ventas por Fecha", "Distribución Menús", "Uso de Ingredientes"],
            command=self.actualizar_combo_periodo, # Evento al cambiar
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
        ctk.CTkButton(frame_ctrl, text="Generar Gráfico", command=self.generar_grafico).pack(side="left", padx=20)

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
            
            messagebox.showinfo("Información", error) # "Mostrar mensaje si no existen registros"
            return

        # 3. Generar Figura
        figura = Graficos.crear_figura(etiquetas, valores, tipo)

        # 4. Incrustar en Tkinter
        if self.canvas_actual:
            self.canvas_actual.get_tk_widget().destroy()

        self.canvas_actual = FigureCanvasTkAgg(figura, master=self.frame_canvas)
        self.canvas_actual.draw()
        self.canvas_actual.get_tk_widget().pack(expand=True, fill="both")

if __name__ == "__main__":
    app = App()
    app.mainloop()
