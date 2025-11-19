import customtkinter as ctk
from tkinter import messagebox, ttk
from database import get_session, engine, Base
from crud.cliente_crud import ClienteCRUD
from crud.pedido_crud import PedidoCRUD
from crud.ingrediente_crud import IngredienteCRUD

# Configuración inicial de CustomTkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Aseguramos que las tablas existan al iniciar
Base.metadata.create_all(bind=engine)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gestión de Restaurante - Evaluación 3")
        self.geometry("900x700")

        # Configuración del Layout Principal
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(pady=10, padx=10, fill="both", expand=True)

        # --- CREACIÓN DE PESTAÑAS ---
        self.tab_clientes = self.tabview.add("Clientes")
        self.tab_ingredientes = self.tabview.add("Stock / Ingredientes")
        self.tab_pedidos = self.tabview.add("Pedidos")

        # Inicializar las interfaces de cada pestaña
        self.crear_interfaz_clientes()
        self.crear_interfaz_ingredientes()
        self.crear_interfaz_pedidos()


    # PESTAÑA 1: GESTIÓN DE CLIENTES
    def crear_interfaz_clientes(self):
        frame = self.tab_clientes
        
        # Formulario
        frame_form = ctk.CTkFrame(frame)
        frame_form.pack(pady=10, padx=10, fill="x")

        self.entry_nombre_cli = ctk.CTkEntry(frame_form, placeholder_text="Nombre Completo")
        self.entry_nombre_cli.pack(side="left", padx=5, expand=True, fill="x")
        
        self.entry_email_cli = ctk.CTkEntry(frame_form, placeholder_text="Email (ID)")
        self.entry_email_cli.pack(side="left", padx=5, expand=True, fill="x")
        
        # CORRECCIÓN AQUÍ: width va dentro del constructor, no en pack
        self.entry_edad_cli = ctk.CTkEntry(frame_form, placeholder_text="Edad", width=80)
        self.entry_edad_cli.pack(side="left", padx=5)

        # Botones
        frame_botones = ctk.CTkFrame(frame, fg_color="transparent")
        frame_botones.pack(pady=5)
        
        ctk.CTkButton(frame_botones, text="Guardar Cliente", command=self.guardar_cliente).pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Actualizar Lista", command=self.cargar_clientes).pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Eliminar Seleccionado", command=self.eliminar_cliente, fg_color="red").pack(side="left", padx=5)

        # Tabla (Treeview)
        columns = ("nombre", "email", "edad")
        self.tree_clientes = ttk.Treeview(frame, columns=columns, show="headings")
        self.tree_clientes.heading("nombre", text="Nombre")
        self.tree_clientes.heading("email", text="Email")
        self.tree_clientes.heading("edad", text="Edad")
        self.tree_clientes.pack(expand=True, fill="both", padx=10, pady=10)

        self.cargar_clientes() # Carga inicial

    def guardar_cliente(self):
        nombre = self.entry_nombre_cli.get()
        email = self.entry_email_cli.get()
        edad_str = self.entry_edad_cli.get()

        if not nombre or not email or not edad_str:
            messagebox.showwarning("Faltan Datos", "Por favor complete todos los campos.")
            return

        try:
            edad = int(edad_str)
        except ValueError:
            messagebox.showerror("Error", "La edad debe ser un número.")
            return

        db = next(get_session())
        nuevo_cliente = ClienteCRUD.crear_cliente(db, nombre, email, edad)
        db.close()

        if nuevo_cliente:
            messagebox.showinfo("Éxito", f"Cliente '{nombre}' guardado.")
            self.limpiar_formulario_cliente()
            self.cargar_clientes()
        else:
            messagebox.showerror("Error", "No se pudo guardar (revise email duplicado o validación).")

    def cargar_clientes(self):
        # Limpiar tabla
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        
        db = next(get_session())
        clientes = ClienteCRUD.leer_clientes(db)
        db.close()

        for c in clientes:
            self.tree_clientes.insert("", "end", values=(c.nombre, c.email, c.edad))

    def eliminar_cliente(self):
        selected = self.tree_clientes.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione un cliente de la lista.")
            return
        
        email = self.tree_clientes.item(selected[0])['values'][1] # El email es la columna 1
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar cliente {email}?"):
            db = next(get_session())
            ClienteCRUD.borrar_cliente(db, email)
            db.close()
            self.cargar_clientes()

    def limpiar_formulario_cliente(self):
        self.entry_nombre_cli.delete(0, 'end')
        self.entry_email_cli.delete(0, 'end')
        self.entry_edad_cli.delete(0, 'end')

    # ==============================================================
    #                   PESTAÑA 2: STOCK / INGREDIENTES
    # ==============================================================
    def crear_interfaz_ingredientes(self):
        frame = self.tab_ingredientes
        
        # Formulario
        frame_form = ctk.CTkFrame(frame)
        frame_form.pack(pady=10, padx=10, fill="x")

        self.entry_nombre_ing = ctk.CTkEntry(frame_form, placeholder_text="Nombre Ingrediente")
        self.entry_nombre_ing.pack(side="left", padx=5, expand=True, fill="x")

        # CORRECCIÓN AQUÍ: width va dentro del constructor
        self.combo_unidad = ctk.CTkComboBox(frame_form, values=["unid", "kg", "lt"], state="readonly", width=80)
        self.combo_unidad.pack(side="left", padx=5)
        self.combo_unidad.set("unid")

        # CORRECCIÓN AQUÍ: width va dentro del constructor
        self.entry_cantidad_ing = ctk.CTkEntry(frame_form, placeholder_text="Cantidad", width=80)
        self.entry_cantidad_ing.pack(side="left", padx=5)

        # Botones
        frame_botones = ctk.CTkFrame(frame, fg_color="transparent")
        frame_botones.pack(pady=5)

        ctk.CTkButton(frame_botones, text="Agregar Ingrediente", command=self.guardar_ingrediente).pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Filtrar Bajo Stock (<5)", command=self.filtrar_bajo_stock, fg_color="orange").pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Eliminar", command=self.eliminar_ingrediente, fg_color="red").pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Refrescar", command=self.cargar_ingredientes).pack(side="left", padx=5)

        # Tabla
        columns = ("id", "nombre", "unidad", "cantidad")
        self.tree_ingredientes = ttk.Treeview(frame, columns=columns, show="headings")
        self.tree_ingredientes.heading("id", text="ID")
        self.tree_ingredientes.heading("nombre", text="Nombre")
        self.tree_ingredientes.heading("unidad", text="Unidad")
        self.tree_ingredientes.heading("cantidad", text="Cantidad")
        self.tree_ingredientes.column("id", width=30)
        self.tree_ingredientes.pack(expand=True, fill="both", padx=10, pady=10)

        self.cargar_ingredientes()

    def guardar_ingrediente(self):
        nombre = self.entry_nombre_ing.get()
        unidad = self.combo_unidad.get()
        cant_str = self.entry_cantidad_ing.get()

        try:
            cantidad = float(cant_str)
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número.")
            return

        db = next(get_session())
        nuevo = IngredienteCRUD.crear_ingrediente(db, nombre, unidad, cantidad)
        db.close()

        if nuevo:
            messagebox.showinfo("Éxito", "Ingrediente agregado.")
            self.entry_nombre_ing.delete(0, 'end')
            self.entry_cantidad_ing.delete(0, 'end')
            self.cargar_ingredientes()
        else:
            messagebox.showerror("Error", "Error al guardar (revise validaciones o duplicados).")

    def cargar_ingredientes(self):
        for item in self.tree_ingredientes.get_children():
            self.tree_ingredientes.delete(item)
        
        db = next(get_session())
        ingredientes = IngredienteCRUD.leer_ingredientes(db)
        db.close()

        for ing in ingredientes:
            self.tree_ingredientes.insert("", "end", values=(ing.id, ing.nombre, ing.unidad, ing.cantidad))

    def filtrar_bajo_stock(self):
        for item in self.tree_ingredientes.get_children():
            self.tree_ingredientes.delete(item)
            
        db = next(get_session())
        bajos = IngredienteCRUD.obtener_ingredientes_bajo_stock(db, umbral=5.0)
        db.close()
        
        for ing in bajos:
             self.tree_ingredientes.insert("", "end", values=(ing.id, ing.nombre, ing.unidad, ing.cantidad))

    def eliminar_ingrediente(self):
        selected = self.tree_ingredientes.selection()
        if not selected: return
        
        id_ing = self.tree_ingredientes.item(selected[0])['values'][0]
        
        db = next(get_session())
        IngredienteCRUD.borrar_ingrediente(db, id_ing)
        db.close()
        self.cargar_ingredientes()

    # ==============================================================
    #                   PESTAÑA 3: PEDIDOS
    # ==============================================================
    def crear_interfaz_pedidos(self):
        frame = self.tab_pedidos

        frame_form = ctk.CTkFrame(frame)
        frame_form.pack(pady=10, padx=10, fill="x")

        self.entry_cliente_email_ped = ctk.CTkEntry(frame_form, placeholder_text="Email del Cliente")
        self.entry_cliente_email_ped.pack(side="left", padx=5, expand=True, fill="x")

        self.entry_desc_ped = ctk.CTkEntry(frame_form, placeholder_text="Descripción del Pedido")
        self.entry_desc_ped.pack(side="left", padx=5, expand=True, fill="x")

        ctk.CTkButton(frame_form, text="Crear Pedido", command=self.crear_pedido).pack(side="left", padx=5)
        ctk.CTkButton(frame_form, text="Actualizar", command=self.cargar_pedidos).pack(side="left", padx=5)
        
        # Nuevo botón para mostrar el cálculo funcional de ventas
        ctk.CTkButton(frame_form, text="Ver Total Ventas (Reduce)", command=self.ver_total_ventas, fg_color="green").pack(side="left", padx=5)

        # Tabla Pedidos
        columns = ("id", "cliente", "descripcion")
        self.tree_pedidos = ttk.Treeview(frame, columns=columns, show="headings")
        self.tree_pedidos.heading("id", text="ID Pedido")
        self.tree_pedidos.heading("cliente", text="Cliente (Email)")
        self.tree_pedidos.heading("descripcion", text="Descripción")
        self.tree_pedidos.pack(expand=True, fill="both", padx=10, pady=10)

        self.cargar_pedidos()

    def crear_pedido(self):
        email = self.entry_cliente_email_ped.get()
        desc = self.entry_desc_ped.get()

        if not email or not desc:
            messagebox.showwarning("Error", "Ingrese email del cliente y descripción.")
            return

        db = next(get_session())
        nuevo_pedido = PedidoCRUD.crear_pedido(db, email, desc)
        db.close()

        if nuevo_pedido:
            messagebox.showinfo("Éxito", "Pedido creado.")
            self.cargar_pedidos()
        else:
            messagebox.showerror("Error", "No se pudo crear (¿Existe el cliente con ese email?).")

    def cargar_pedidos(self):
        for item in self.tree_pedidos.get_children():
            self.tree_pedidos.delete(item)

        db = next(get_session())
        pedidos = PedidoCRUD.leer_pedidos(db)
        db.close()

        for p in pedidos:
            self.tree_pedidos.insert("", "end", values=(p.id, p.cliente_email, p.descripcion))
            
    def ver_total_ventas(self):
        db = next(get_session())
        total = PedidoCRUD.calcular_total_ventas(db)
        db.close()
        messagebox.showinfo("Cálculo Funcional", f"El total estimado de ventas (usando Reduce) es: ${total:,.0f}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
