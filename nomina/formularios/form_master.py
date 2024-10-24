import os
import tkinter as tk
from tkinter import ttk, messagebox
from util.db_manager import DatabaseManager
from util.config import DB_CONFIG
from datetime import datetime
from decimal import Decimal
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.db_manager = DatabaseManager(**DB_CONFIG)

        # Configuración de la ventana principal
        self.title("Sistema de Nómina - R.H.G Inversiones, C.A.")
        self.geometry("600x400")

        # Crear barra de menú
        self.create_menu()

        # Aquí añades los widgets de la aplicación principal
        self.label = tk.Label(self, text="Bienvenido al Sistema de Nómina de R.H.G Inversiones")
        self.label.pack(pady=20, padx=20)

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # Menú Empleados
        empleados_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Empleados", menu=empleados_menu)
        empleados_menu.add_command(label="Registrar Empleado", command=self.registrar_empleado)
        empleados_menu.add_command(label="Ver Empleados", command=self.ver_empleados)
        
        # Menú Nómina
        nomina_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Nómina", menu=nomina_menu)
        nomina_menu.add_command(label="Generar Prenómina", command=self.ver_prenominas)
        # nomina_menu.add_command(label="Editar Prenómina", command=self.editar_prenomina)
        # nomina_menu.add_command(label="Generar Nómina", command=self.generar_nomina)

        # Menú Reportes
        nomina_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reportes", menu=nomina_menu)
        nomina_menu.add_command(label="Ver Reporte de Nómina", command=self.ver_reportes_nomina)
        nomina_menu.add_command(label="Ver Reporte de Asistencia", command=self.ver_reporte_asistencia)
        
        # Menú Salir
        menubar.add_command(label="Salir", command=self.confirmar_salir)

    def registrar_empleado(self):
        # Crear una nueva ventana para el registro de empleados
        form = tk.Toplevel(self)
        form.title("Registrar Empleado")
        form.geometry("500x500")
        
        # Etiquetas y campos de texto para registrar al empleado
        tk.Label(form, text="Nombre:").pack(pady=5)
        nombre_entry = tk.Entry(form)
        nombre_entry.pack(pady=5)

        tk.Label(form, text="Apellido:").pack(pady=5)
        apellido_entry = tk.Entry(form)
        apellido_entry.pack(pady=5)

        tk.Label(form, text="Cédula:").pack(pady=5)
        cedula_entry = tk.Entry(form)
        cedula_entry.pack(pady=5)

        tk.Label(form, text="Cargo:").pack(pady=5)
        cargo_var = tk.StringVar(form)
        cargo_var.set("Seleccione un cargo")  # Valor inicial
        opciones_cargo = ["Gerente", "Empleado"]
        cargo_menu = tk.OptionMenu(form, cargo_var, *opciones_cargo)
        cargo_menu.pack(pady=5)

        tk.Label(form, text="Salario:").pack(pady=5)
        salario_entry = tk.Entry(form)
        salario_entry.pack(pady=5)

        tk.Label(form, text="UID NFC:").pack(pady=5)
        uid_nfc_entry = tk.Entry(form)
        uid_nfc_entry.pack(pady=5)

        tk.Label(form, text="Fecha de Contratación (YYYY-MM-DD):").pack(pady=5)
        fecha_contratacion_entry = tk.Entry(form)
        fecha_contratacion_entry.pack(pady=5)


        # Botón para guardar los datos
        def guardar_empleado():
            nombre = nombre_entry.get()
            apellido = apellido_entry.get()
            cedula = cedula_entry.get()
            cargo = cargo_var.get()
            salario = salario_entry.get()
            uid_nfc = uid_nfc_entry.get()
            fecha_contratacion = fecha_contratacion_entry.get()

            if nombre and apellido and cedula and cargo and salario and uid_nfc and fecha_contratacion:
                # Verificar si ya existe un empleado con la misma cédula o UID NFC
                if self.db_manager.verificar_empleado_existente(cedula, uid_nfc):
                    messagebox.showerror("Error", "Ya existe un empleado con la misma cédula o UID NFC")
                else:
                    self.db_manager.registrar_empleado(nombre, cargo, salario, uid_nfc, fecha_contratacion, cedula, apellido)
                    messagebox.showinfo("Empleado Registrado", "Empleado registrado exitosamente")
                    form.destroy()
            else:
                messagebox.showerror("Error", "Por favor, llena todos los campos")

        tk.Button(form, text="Guardar", command=guardar_empleado).pack(pady=10)

    def ver_empleados(self):
        # Crear una nueva ventana para mostrar los empleados
        empleados_window = tk.Toplevel(self)
        empleados_window.title("Empleados Registrados")
        empleados_window.geometry("1000x600")

        # Configurar el peso de las filas y columnas para hacer la ventana responsive
        empleados_window.grid_rowconfigure(0, weight=1)
        empleados_window.grid_columnconfigure(0, weight=1)

        # Frame principal
        main_frame = ttk.Frame(empleados_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        ttk.Label(title_frame, text="Lista de Empleados", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)

        # Frame de búsqueda
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=1, column=0, pady=(0, 10), sticky=(tk.W, tk.E))

        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Crear Treeview
        tree = ttk.Treeview(main_frame, columns=("ID", "Nombre", "Apellido", "Cedula", "Cargo", "Salario", "Fecha_Contratacion"), show='headings')
        
        # Configurar las columnas
        tree.heading("ID", text="ID")
        tree.heading("Nombre", text="Nombre")
        tree.heading("Apellido", text="Apellido")
        tree.heading("Cedula", text="Cédula")
        tree.heading("Cargo", text="Cargo")
        tree.heading("Salario", text="Salario")
        tree.heading("Fecha_Contratacion", text="Fecha Contratación")
        
        # Configurar el ancho de las columnas
        tree.column("ID", width=50)
        tree.column("Nombre", width=150)
        tree.column("Apellido", width=150)
        tree.column("Cedula", width=100)
        tree.column("Cargo", width=150)
        tree.column("Salario", width=100)
        tree.column("Fecha_Contratacion", width=150)

        # Crear scrollbars
        vsb = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(main_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Posicionar el Treeview y scrollbars
        tree.grid(row=2, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        vsb.grid(row=2, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=3, column=0, sticky=(tk.E, tk.W))

        # Cargar datos de la base de datos
        empleados = self.db_manager.ver_empleados()
        if empleados:
            # Insertar empleados en el Treeview
            for emp in empleados:
                tree.insert('', 'end', values=(emp[0], emp[1], emp[2], emp[3], emp[4], f"{emp[5]:,.2f}", emp[6]))
        else:
            messagebox.showinfo("Información", "No hay empleados registrados.")

        # Filtrar empleados
        def filter_treeview(*args):
            search_text = search_var.get().lower()
            
            # Limpiar el Treeview
            for item in tree.get_children():
                tree.delete(item)
            
            # Filtrar y mostrar coincidencias
            for emp in empleados:
                if any(str(value).lower().find(search_text) >= 0 for value in emp):
                    tree.insert('', 'end', values=(emp[0], emp[1], emp[2], emp[3], emp[4], f"{emp[5]:,.2f}", emp[6]))
        
        search_var.trace('w', filter_treeview)

        # Botón para cerrar la ventana
        ttk.Button(main_frame, text="Cerrar", command=empleados_window.destroy).grid(row=4, column=0, pady=10, sticky=(tk.E))

    def ver_prenominas(self):
        # Crear una nueva ventana para mostrar las prenóminas
        prenominas_window = tk.Toplevel(self)
        prenominas_window.title("Prenóminas de Empleados")
        prenominas_window.geometry("900x455")

        # Configurar el peso de las filas y columnas para hacer la ventana responsive
        prenominas_window.grid_rowconfigure(0, weight=1)
        prenominas_window.grid_columnconfigure(0, weight=1)

        # Frame principal
        main_frame = ttk.Frame(prenominas_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        ttk.Label(title_frame, text="Prenóminas de Empleados", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)

        # Frame de búsqueda y filtros
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=1, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        
        ttk.Label(search_frame, text="Buscar: ").pack(side=tk.LEFT, padx=(0, 5))
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side=tk.LEFT)

        # Definir columnas y sus nombres visibles
        columns = [
            ("nombre", "Nombre"),
            ("apellido", "Apellido"),
            ("cedula", "Cédula"),
            ("cargo", "Cargo"),
            ("salario_base", "Salario Base"),
            ("seguro_social", "Seguro Social"),
            ("rpe", "RPE"),
            ("ley_pol_hab", "Ley Pol. Hab."),
            ("inasistencias", "Inasistencias"),
            ("prestamos", "Préstamos"),
            ("total_deducciones", "Total Deducciones"),
            ("total_a_pagar", "Total a Pagar")
        ]

        # # Crear Treeview
        # tree = ttk.Treeview(main_frame, columns=[col[0] for col in columns], show='headings')
        
        # # Configurar las columnas
        # for col, text in columns:
        #     tree.heading(col, text=text)
        #     tree.column(col, width=100)  # Ajusta este valor según sea necesario

        # # Crear scrollbars
        # vsb = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
        # hsb = ttk.Scrollbar(main_frame, orient="horizontal", command=tree.xview)
        # tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # # Posicionar el Treeview y scrollbars
        # tree.grid(row=2, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        # vsb.grid(row=2, column=1, sticky=(tk.N, tk.S))
        # hsb.grid(row=3, column=0, sticky=(tk.E, tk.W))

        # Crear Treeview
        self.prenominas_tree = ttk.Treeview(main_frame, columns=[col[0] for col in columns], show='headings')
        
        # Configurar las columnas
        for col, text in columns:
            self.prenominas_tree.heading(col, text=text)
            self.prenominas_tree.column(col, width=100)  # Ajusta este valor según sea necesario

        # Crear scrollbars
        vsb = ttk.Scrollbar(main_frame, orient="vertical", command=self.prenominas_tree.yview)
        hsb = ttk.Scrollbar(main_frame, orient="horizontal", command=self.prenominas_tree.xview)
        self.prenominas_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Posicionar el Treeview y scrollbars
        self.prenominas_tree.grid(row=2, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        vsb.grid(row=2, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=3, column=0, sticky=(tk.E, tk.W))

        # Cargar datos de la base de datos
        empleados = self.db_manager.ver_empleados()
        prenominas = []

        if empleados:
            for emp in empleados:
                # Calcular la prenómina para cada empleado
                salario_base_mensual = Decimal(str(emp[5]))
                salario_base_quincenal = salario_base_mensual / Decimal('2')
                deducciones = self.db_manager.obtener_deducciones_empleado(emp[0])
                
                seguro_social = Decimal('0')
                rpe = Decimal('0')
                ley_pol_hab = Decimal('0')
                
                total_deducciones = Decimal('0')
                for deduccion in deducciones:
                    nombre, porcentaje, tipo, _ = deduccion  # Ignoramos el monto de la base de datos
                    porcentaje = Decimal(str(porcentaje))  # Aseguramos que porcentaje sea Decimal
                    
                    if nombre == "Seguro Social" or nombre == "RPE":
                        monto_deduccion = (salario_base_mensual * Decimal('12') / Decimal('52')) * porcentaje * Decimal('2')
                        if nombre == "Seguro Social":
                            seguro_social = monto_deduccion
                        else:
                            rpe = monto_deduccion
                    elif nombre == "Ley de Política Habitacional":
                        monto_deduccion = (((salario_base_quincenal / Decimal('30')) * (Decimal('45') / Decimal('12')) + salario_base_quincenal)) * porcentaje
                        ley_pol_hab = monto_deduccion
                    else:
                        # Para cualquier otra deducción, usamos el cálculo simple
                        monto_deduccion = salario_base_quincenal * porcentaje
                    
                    total_deducciones += monto_deduccion

                # Obtener inasistencias y préstamos (asumiendo que tienes métodos para esto)
                inasistencias = self.db_manager.obtener_inasistencias_empleado(emp[0])
                prestamos = self.db_manager.obtener_prestamos_empleado(emp[0])

                inasistencias_valor = Decimal(str(inasistencias)) * (salario_base_mensual / Decimal('30'))
                prestamos_valor = Decimal(str(prestamos))

                total_deducciones = seguro_social + rpe + ley_pol_hab + inasistencias_valor + prestamos_valor
                total_a_pagar = salario_base_quincenal - total_deducciones

                prenomina = (emp[1], emp[2], emp[3], emp[4], salario_base_quincenal,
                            seguro_social, rpe, ley_pol_hab, inasistencias_valor,
                            prestamos_valor, total_deducciones, total_a_pagar)
                prenominas.append(prenomina)

                # Insertar prenóminas en el Treeview
                self.prenominas_tree.insert('', 'end', values=[f"{val:,.2f}" if isinstance(val, Decimal) else val for val in prenomina])
        else:
            messagebox.showinfo("Información", "No hay empleados registrados.")

        # Filtrar prenóminas
        def filter_treeview(*args):
            search_text = search_var.get().lower()
            
            # Limpiar el Treeview
            for item in self.prenominas_tree.get_children():
                self.prenominas_tree.delete(item)
            
            # Filtrar y mostrar coincidencias
            for prenomina in prenominas:
                if any(str(value).lower().find(search_text) >= 0 for value in prenomina):
                    self.prenominas_tree.insert('', 'end', values=[f"{val:,.2f}" if isinstance(val, Decimal) else val for val in prenomina])
        
        search_var.trace('w', filter_treeview)

        # Frame para los botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, pady=10, sticky=(tk.W, tk.E))

        # Botón para cerrar la ventana
        ttk.Button(button_frame, text="Cerrar", command=prenominas_window.destroy).pack(side=tk.LEFT, padx=5)

        # Botón para editar prenómina
        ttk.Button(button_frame, text="Editar Prenómina", command=self.editar_prenomina).pack(side=tk.LEFT, padx=5)

        # Botón para generar nómina
        ttk.Button(button_frame, text="Generar Nómina", command=self.generar_nominas_pdf).pack(side=tk.LEFT, padx=5)

    def editar_prenomina(self):
        # Crear ventana para la prenómina
        prenomina_window = tk.Toplevel(self)
        prenomina_window.title("Sistema de Prenómina - R.H.G Inversiones, C.A.")
        prenomina_window.geometry("800x600")

        # Frame principal
        main_frame = ttk.Frame(prenomina_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame para selección de empleado
        selector_frame = ttk.LabelFrame(main_frame, text="Selección de Empleado", padding="5")
        selector_frame.pack(fill=tk.X, padx=10, pady=5)

        # Combobox para seleccionar empleado
        ttk.Label(selector_frame, text="Empleado:").pack(side=tk.LEFT, padx=5)
        empleado_var = tk.StringVar()
        combo_empleados = ttk.Combobox(selector_frame, 
                                    textvariable=empleado_var,
                                    state="readonly",
                                    width=40)
        combo_empleados.pack(side=tk.LEFT, padx=5)

        # Cargar empleados desde la base de datos
        empleados = self.db_manager.ver_empleados()
        if empleados:
            combo_empleados['values'] = [f"{emp[1]} {emp[2]} - CI: {emp[3]}" for emp in empleados]

        # Frame para mostrar la prenómina
        prenomina_frame = ttk.Frame(main_frame)
        prenomina_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        def cargar_prenomina():
            # Limpiar frame anterior
            for widget in prenomina_frame.winfo_children():
                widget.destroy()

            # Obtener empleado seleccionado
            if not empleado_var.get():
                messagebox.showwarning("Advertencia", "Por favor seleccione un empleado")
                return

            # Encontrar el empleado seleccionado
            empleado_seleccionado = None
            for emp in empleados:
                if f"{emp[1]} {emp[2]} - CI: {emp[3]}" == empleado_var.get():
                    empleado_seleccionado = emp
                    break

            if not empleado_seleccionado:
                return

            # Mostrar prenómina del empleado seleccionado
            mostrar_prenomina_detalle(empleado_seleccionado)

        def mostrar_prenomina_detalle(empleado):
            # Limpiar frame anterior
            for widget in prenomina_frame.winfo_children():
                widget.destroy()

            # Encabezado
            ttk.Label(prenomina_frame, 
                    text="PRENÓMINA", 
                    font=('Arial', 16, 'bold')).pack(pady=10)

            # Contenedor principal para los datos
            content_frame = ttk.Frame(prenomina_frame)
            content_frame.pack(fill=tk.BOTH, expand=True)

            # Columna izquierda
            left_column = ttk.Frame(content_frame)
            left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

            # Columna derecha
            right_column = ttk.Frame(content_frame)
            right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

            # Datos de la empresa (columna izquierda)
            empresa_frame = ttk.LabelFrame(left_column, text="Datos de la Empresa", padding="5")
            empresa_frame.pack(fill=tk.X, pady=5)
            ttk.Label(empresa_frame, text="Empresa: R.H.G Inversiones, C.A.").pack(anchor=tk.W)
            ttk.Label(empresa_frame, text="RIF: J-31347691-9").pack(anchor=tk.W)
            ttk.Label(empresa_frame, text=f"Fecha: {datetime.now().strftime('%d/%m/%Y')}").pack(anchor=tk.W)

            # Datos del empleado (columna izquierda)
            empleado_frame = ttk.LabelFrame(left_column, text="Datos del Empleado", padding="5")
            empleado_frame.pack(fill=tk.X, pady=5)
            ttk.Label(empleado_frame, text=f"Nombre: {empleado[1]} {empleado[2]}").pack(anchor=tk.W)
            ttk.Label(empleado_frame, text=f"Cédula: {empleado[3]}").pack(anchor=tk.W)
            ttk.Label(empleado_frame, text=f"Cargo: {empleado[4]}").pack(anchor=tk.W)

            # Conceptos Salariales (columna derecha)
            salario_base_mensual = Decimal(str(empleado[5]))
            salario_base_quincenal = salario_base_mensual / Decimal('2')
            salario_base_diario = salario_base_mensual / Decimal ('30')
            conceptos_frame = ttk.LabelFrame(right_column, text="Conceptos Salariales", padding="5")
            conceptos_frame.pack(fill=tk.X, pady=5)

            # Salario Base Mensual
            salario_mensual_frame = ttk.Frame(conceptos_frame)
            salario_mensual_frame.pack(fill=tk.X)
            ttk.Label(salario_mensual_frame, text="Salario Base Mensual").pack(side=tk.LEFT, padx=(0, 10))
            ttk.Label(salario_mensual_frame, text=f"{salario_base_mensual:,.2f} Bs.").pack(side=tk.RIGHT)

            # Salario Base Quincenal
            salario_diario_frame = ttk.Frame(conceptos_frame)
            salario_diario_frame.pack(fill=tk.X)
            ttk.Label(salario_diario_frame, text="Salario Base Diario").pack(side=tk.LEFT, padx=(0, 10))
            ttk.Label(salario_diario_frame, text=f"{salario_base_diario:,.2f} Bs.").pack(side=tk.RIGHT)
            
            # Deducciones (columna derecha)
            deducciones_frame = ttk.LabelFrame(right_column, text="Deducciones", padding="5")
            deducciones_frame.pack(fill=tk.X, pady=5)
            
            # Obtener las deducciones del empleado desde la base de datos
            deducciones = self.db_manager.obtener_deducciones_empleado(empleado[0])
            
            total_deducciones = Decimal('0')
            for deduccion in deducciones:
                nombre, porcentaje, tipo, _ = deduccion  # Ignoramos el monto de la base de datos
                porcentaje = Decimal(str(porcentaje))  # Aseguramos que porcentaje sea Decimal
                
                if nombre == "Seguro Social" or nombre == "RPE":
                    monto_deduccion = (salario_base_mensual * Decimal('12') / Decimal('52')) * porcentaje * Decimal('2')
                elif nombre == "Ley de Política Habitacional":
                    monto_deduccion = (((salario_base_quincenal / Decimal('30')) * (Decimal('45') / Decimal('12')) + salario_base_quincenal)) * porcentaje
                else:
                    # Para cualquier otra deducción, usamos el cálculo simple
                    monto_deduccion = salario_base_quincenal * porcentaje
                
                total_deducciones += monto_deduccion
                
                deduccion_frame = ttk.Frame(deducciones_frame)
                deduccion_frame.pack(fill=tk.X)
                ttk.Label(deduccion_frame, text=f"{nombre}:").pack(side=tk.LEFT)
                ttk.Label(deduccion_frame, text=f"{monto_deduccion:,.2f} Bs.").pack(side=tk.RIGHT)
            
            # Total (abajo)
            total_frame = ttk.LabelFrame(prenomina_frame, text="Totales", padding="5")
            total_frame.pack(fill=tk.X, padx=10, pady=5)
            
            total_deducciones_frame = ttk.Frame(total_frame)
            total_deducciones_frame.pack(fill=tk.X)
            ttk.Label(total_deducciones_frame, text="Total Deducciones:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
            ttk.Label(total_deducciones_frame, text=f"{total_deducciones:,.2f} Bs.", font=('Arial', 10, 'bold')).pack(side=tk.RIGHT)
            
            # Calcular el salario neto
            salario_neto = salario_base_quincenal - total_deducciones
            
            total_pagar_frame = ttk.Frame(total_frame)
            total_pagar_frame.pack(fill=tk.X)
            ttk.Label(total_pagar_frame, text="Total a Pagar:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
            ttk.Label(total_pagar_frame, text=f"{salario_neto:,.2f} Bs.", font=('Arial', 10, 'bold')).pack(side=tk.RIGHT)

            # Botones de acción
            buttons_frame = ttk.Frame(prenomina_frame)
            buttons_frame.pack(pady=10)
            ttk.Button(buttons_frame, text="Generar Nómina Empleado",
                    command=lambda: messagebox.showinfo("Generar Nómina", "Función de generar Nómina pendiente")).pack()

        # Botón para cargar prenómina
        ttk.Button(selector_frame, 
                text="Cargar Prenómina", 
                command=cargar_prenomina).pack(side=tk.LEFT, padx=5)

    def generar_nomina(self):
        if messagebox.askyesno("Generar Nómina", "¿Estás seguro que deseas generar la nómina?"):
            self.db_manager.generar_nomina()
            messagebox.showinfo("Nómina Generada", "Nómina generada exitosamente")
    
    def ver_reportes_nomina(self):
        # Aquí irá la lógica para mostrar los reportes de nómina
        messagebox.showinfo("Reportes de Nómina", "Reportes de nómina generados")

    def ver_reporte_asistencia(self):
        # Aquí irá la lógica para mostrar los reportes de asistencia
        messagebox.showinfo("Reporte de Asistencia", "Reporte de asistencia generado")

    def confirmar_salir(self):
        if messagebox.askokcancel("Salir", "¿Estás seguro que deseas salir?"):
            self.destroy()
    
    def generar_nominas_pdf(self):
         # Verificar si el Treeview existe
        if not hasattr(self, 'prenominas_tree'):
            messagebox.showerror("Error", "La tabla de prenóminas no está disponible.")
            return
        
        # Crear una carpeta para los PDFs si no existe
        output_folder = "nominas_pdf"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Obtener todos los items del Treeview
        all_items = self.prenominas_tree.get_children()
        total_empleados = len(all_items)
        empleados_procesados = 0

        for item in all_items:
            empleado_data = self.prenominas_tree.item(item)['values']
            
                # Convertir y validar los datos
            try:
                nombre = str(empleado_data[0])
                apellido = str(empleado_data[1])
                cedula = str(empleado_data[2])
                cargo = str(empleado_data[3])
                sueldo = float(empleado_data[4].replace(',', '')) if isinstance(empleado_data[4], str) else float(empleado_data[4])
                seguro_social = float(empleado_data[5].replace(',', '')) if isinstance(empleado_data[5], str) else float(empleado_data[5])
                rpe = float(empleado_data[6].replace(',', '')) if isinstance(empleado_data[6], str) else float(empleado_data[6])
                ley_pol_hab = float(empleado_data[7].replace(',', '')) if isinstance(empleado_data[7], str) else float(empleado_data[7])
                inasistencias = float(empleado_data[8].replace(',', '')) if isinstance(empleado_data[8], str) else float(empleado_data[8])
                prestamos = float(empleado_data[9].replace(',', '')) if isinstance(empleado_data[9], str) else float(empleado_data[9])
            except (IndexError, ValueError) as e:
                print(f"Error procesando datos del empleado: {e}")
                continue

            pdf_filename = os.path.join(output_folder, f"nomina_{cedula}.pdf")
            doc = SimpleDocTemplate(pdf_filename, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
            elements = []

            styles = getSampleStyleSheet()
            title_style = styles['Title']
            title_style.alignment = 1  # Centrado

            elements.append(Paragraph("R.H.G. INVERSIONES, C.A.", title_style))
            elements.append(Paragraph("COMPROBANTE DE PAGO", title_style))
            elements.append(Paragraph("DATOS DEL TRABAJADOR", title_style))
            elements.append(Spacer(1, 0.25*inch))

            data = [
                ["Sueldo", "Apellidos y Nombres", "Cédula"],
                [f"{sueldo:,.2f}", f"{nombre} {apellido}", cedula],
                ["Cargo", "Unidad de Adscripción", ""],
                [cargo, "Administración", ""]
            ]

            data.extend([
                ["Concepto", "Referencia", "Asignación", "Deducción"],
                ["DIAS TRABAJADOS", "15", f"{sueldo:,.2f}", ""],
                ["SEGURO SOCIAL OBLIGATORIO", "2", "", f"{seguro_social:,.2f}"],
                ["REGIMEN PRESTACIONAL DE EMPLEO", "2", "", f"{rpe:,.2f}"],
                ["FONDO DE AHORRO OBLIGATORIO P/VIVIENDA", "0.01", "", f"{ley_pol_hab:,.2f}"],
                ["INASISTENCIAS", "", "", f"{inasistencias:,.2f}"],
                ["PRÉSTAMOS", "", "", f"{prestamos:,.2f}"]
            ])

            total_asignaciones = sueldo
            total_deducciones = seguro_social + rpe + ley_pol_hab + inasistencias + prestamos
            neto_a_cobrar = total_asignaciones - total_deducciones

            data.extend([
                ["Total Asignaciones y Deducciones", "", f"{total_asignaciones:,.2f}", f"{total_deducciones:,.2f}"],
                ["Período: DEL 01/09 AL 15/09/2024", "Neto a Cobrar", f"{neto_a_cobrar:,.2f}", ""]
            ])

            # Crear la tabla
            t = Table(data, colWidths=[2.5*inch, 2*inch, 1.5*inch, 1.5*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            elements.append(t)

            # Añadir firma
            elements.append(Spacer(1, 0.5*inch))
            elements.append(Paragraph("Declaro haber recibido conforme el monto que me corresponde para el período según los indicado por los conceptos especificados en este recibo de pago.", styles['Normal']))
            elements.append(Spacer(1, 0.25*inch))
            elements.append(Paragraph("Firma: _______________________", styles['Normal']))
            elements.append(Paragraph("Cédula: ______________________", styles['Normal']))

            # Construir el PDF
            doc.build(elements)
            
            empleados_procesados += 1
            # Actualizar la barra de progreso o mostrar avance
            print(f"Procesado {empleados_procesados} de {total_empleados}")

        messagebox.showinfo("PDFs Generados", f"Se han generado {total_empleados} archivos PDF de nómina en la carpeta '{output_folder}'")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()