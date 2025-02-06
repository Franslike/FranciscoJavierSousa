import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from util.ayuda import Ayuda

class PeriodoNominaForm(ttk.Frame):
    def __init__(self, parent, db_manager, usuario_actual):
        super().__init__(parent)
        self.db_manager = db_manager
        self.usuario_actual = usuario_actual
        self.sistema_ayuda = Ayuda()

        self.bind_all("<F1>", self.mostrar_ayuda)
        
        self.pack(fill=tk.BOTH, expand=True)

        # Verificar permisos
        alcance = self.db_manager.verificar_permiso(
            usuario_actual['id_usuario'], 
            'periodos.gestion'
        )

        if not alcance or alcance != 'GLOBAL':
            messagebox.showerror("Error", "No tienes los permisos suficientes para ingresar a este módulo.")
            self.destroy()
            return
        
        # Frame principal
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Titulo
        ttk.Label(self.main_frame, text="Gestión de Periodos", font=('Helvetica', 12, 'bold')).pack(anchor='w', pady=(0,5))
        
        # Frame para crear nuevo período
        self.crear_periodo_frame = ttk.LabelFrame(self.main_frame, text="Crear Nuevo Período", padding="10")
        self.crear_periodo_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Tipo de período
        ttk.Label(self.crear_periodo_frame, text="Tipo de Período:").grid(row=0, column=0, padx=5, pady=5)
        self.tipo_var = tk.StringVar(value="Quincenal")
        tipo_combo = ttk.Combobox(self.crear_periodo_frame, 
                                 textvariable=self.tipo_var,
                                 values=["Quincenal", "Mensual", "Semanal"],
                                 state="readonly")
        tipo_combo.grid(row=0, column=1, padx=5, pady=5)
        tipo_combo.bind("<<ComboboxSelected>>", self.actualizar_fechas)
        
        # Fecha inicio
        ttk.Label(self.crear_periodo_frame, text="Fecha Inicio:").grid(row=1, column=0, padx=5, pady=5)
        self.fecha_inicio = DateEntry(self.crear_periodo_frame, width=12, background='darkblue',
                                    date_pattern='dd/mm/yyyy', foreground='white', borderwidth=2)
        self.fecha_inicio.grid(row=1, column=1, padx=5, pady=5)
        self.fecha_inicio.bind("<<DateEntrySelected>>", self.actualizar_fecha_fin)
        
        # Fecha fin
        ttk.Label(self.crear_periodo_frame, text="Fecha Fin:").grid(row=2, column=0, padx=5, pady=5)
        self.fecha_fin = DateEntry(self.crear_periodo_frame, width=12, background='darkblue',
                                 date_pattern='dd/mm/yyyy', foreground='white', borderwidth=2)
        self.fecha_fin.grid(row=2, column=1, padx=5, pady=5)
        
        # Botón crear período
        ttk.Button(self.crear_periodo_frame, text="Crear Período",
                  command=self.crear_periodo).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Frame para lista de períodos
        self.lista_periodos_frame = ttk.LabelFrame(self.main_frame, text="Períodos Existentes", padding="10")
        self.lista_periodos_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Crear Treeview para mostrar períodos
        self.tree = ttk.Treeview(self.lista_periodos_frame, columns=(
            "id", "tipo", "fecha_inicio", "fecha_fin", "estado", "creado_por"), 
            show='headings', displaycolumns=("tipo", "fecha_inicio", "fecha_fin", "estado", "creado_por"))
        
        # Configurar columnas
        self.tree.column("id", width=0, stretch=False)
        self.tree.column("tipo", width=100)
        self.tree.column("fecha_inicio", width=100)
        self.tree.column("fecha_fin", width=100)
        self.tree.column("estado", width=100)
        self.tree.column("creado_por", width=100)

        # Configurar encabezados
        self.tree.heading("id", text="ID")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("fecha_inicio", text="Fecha Inicio")
        self.tree.heading("fecha_fin", text="Fecha Fin")
        self.tree.heading("estado", text="Estado")
        self.tree.heading("creado_por", text="Creado Por")

        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(self.lista_periodos_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Empacar Treeview y scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame para acciones de períodos
        self.acciones_frame = ttk.Frame(self.main_frame)
        self.acciones_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Botones de acción
        ttk.Button(self.acciones_frame, text="Cerrar Período",
                  command=self.cerrar_periodo).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.acciones_frame, text="Actualizar Lista",
                  command=self.cargar_periodos).pack(side=tk.LEFT, padx=5)
        
        # Cargar períodos existentes
        self.cargar_periodos()
        
        # Bind para el evento de selección
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Variable para almacenar el período seleccionado
        self.periodo_seleccionado = None

    def mostrar_ayuda(self, event=None):
        """Muestra la ayuda contextual del módulo de empleados"""
        self.sistema_ayuda.mostrar_ayuda('periodos')

    def actualizar_fechas(self, event=None):
        """Actualizar las fechas cuando cambia el tipo de período"""
        if self.fecha_inicio.get_date():
            self.actualizar_fecha_fin()

    def actualizar_fecha_fin(self, event=None):
        """Calcular y establecer la fecha de fin basada en el tipo de período"""
        fecha_inicio = self.fecha_inicio.get_date()
        tipo = self.tipo_var.get()
        
        if not fecha_inicio:
            return
        
        from datetime import datetime, timedelta, date
        import calendar
        
        nueva_fecha_fin = None
        
        if tipo == "Quincenal":
            if fecha_inicio.day == 1:
                # Si empieza el 1, termina el 15
                nueva_fecha_fin = fecha_inicio.replace(day=15)
            elif fecha_inicio.day == 16:
                # Si empieza el 16, termina el último día del mes
                ultimo_dia = calendar.monthrange(fecha_inicio.year, fecha_inicio.month)[1]
                nueva_fecha_fin = fecha_inicio.replace(day=ultimo_dia)
            
        elif tipo == "Mensual":
            if fecha_inicio.day == 1:
                # Último día del mes
                ultimo_dia = calendar.monthrange(fecha_inicio.year, fecha_inicio.month)[1]
                nueva_fecha_fin = fecha_inicio.replace(day=ultimo_dia)
                
        elif tipo == "Semanal":
            # Agregar 6 días a la fecha de inicio (para completar 7 días)
            nueva_fecha_fin = fecha_inicio + timedelta(days=6)
        
        if nueva_fecha_fin:
            self.fecha_fin.set_date(nueva_fecha_fin)

    def crear_periodo(self):
        """Crear un nuevo período de nómina"""
        try:
            fecha_inicio = self.fecha_inicio.get_date()
            fecha_fin = self.fecha_fin.get_date()
            tipo = self.tipo_var.get()
            
            # Validaciones básicas
            if fecha_inicio >= fecha_fin:
                messagebox.showerror("Error", "La fecha de inicio debe ser anterior a la fecha de fin")
                return
            
            # Calcular la diferencia en días
            diferencia_dias = (fecha_fin - fecha_inicio).days + 1
            
            # Validar duración según el tipo de período
            if tipo == "Quincenal":
                if diferencia_dias > 15:
                    messagebox.showerror("Error", 
                        "Un período quincenal no puede tener más de 15 días.\n"
                        f"Días seleccionados: {diferencia_dias}")
                    return
                # Validar que comience el 1 o 16 del mes
                if fecha_inicio.day not in [1, 16]:
                    messagebox.showerror("Error", 
                        "Un período quincenal debe comenzar el día 1 o 16 del mes")
                    return
                
            elif tipo == "Mensual":
                if diferencia_dias > 31:
                    messagebox.showerror("Error", 
                        "Un período mensual no puede tener más de 31 días.\n"
                        f"Días seleccionados: {diferencia_dias}")
                    return
                # Validar que comience el primer día del mes
                if fecha_inicio.day != 1:
                    messagebox.showerror("Error", 
                        "Un período mensual debe comenzar el primer día del mes")
                    return
                
            elif tipo == "Semanal":
                if diferencia_dias > 7:
                    messagebox.showerror("Error", 
                        "Un período semanal no puede tener más de 7 días.\n"
                        f"Días seleccionados: {diferencia_dias}")
                    return
                # Validar que comience en lunes
                if fecha_inicio.weekday() != 0:  # 0 representa el lunes
                    messagebox.showerror("Error", 
                        "Un período semanal debe comenzar en lunes")
                    return
            
            # Validar que no haya períodos que se solapen o abiertos
            hay_solapamiento, mensaje = self.db_manager.verificar_solapamiento_periodos(fecha_inicio, fecha_fin)
            if hay_solapamiento:
                messagebox.showerror("Error", mensaje)
                return
            
            # Si todas las validaciones pasan, crear el período
            self.db_manager.crear_periodo(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                tipo=tipo,
                creado_por=f"{self.usuario_actual['nombre']} {self.usuario_actual['apellido']}")
            # Detalles para auditoria
            detalle = (f"Creación de período:\n"
                       f"Tipo: {tipo}\n"
                       f"Fecha Inicio: {fecha_inicio}\n"
                       f"Fecha Fin: {fecha_fin}\n"
                       f"Registrado por: {self.usuario_actual['nombre']} {self.usuario_actual['apellido']}")

            self.db_manager.registrar_auditoria(
                usuario=f"{self.usuario_actual['nombre']} {self.usuario_actual['apellido']}",
                rol=f"{self.usuario_actual['rol']}",
                accion='Creó período',
                tabla='periodos_nomina',
                detalle=detalle)
            
            messagebox.showinfo("Éxito", "Período creado correctamente")
            self.cargar_periodos()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear el período: {str(e)}")

    def cargar_periodos(self):
        """Cargar los períodos existentes en el Treeview"""
        # Limpiar Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Obtener períodos de la base de datos
        periodos = self.db_manager.obtener_periodos()
        
        # Insertar períodos en el Treeview
        for periodo in periodos:
            self.tree.insert('', 'end', values=periodo)

    def cerrar_periodo(self):
        """Cerrar el período seleccionado"""
        if not self.periodo_seleccionado:
            messagebox.showwarning("Advertencia", "Por favor seleccione un período")
            return
            
        if messagebox.askyesno("Confirmar", "¿Está seguro de cerrar este período?"):
            try:
                self.db_manager.cerrar_periodo(
                    self.periodo_seleccionado,
                    cerrado_por=f"{self.usuario_actual['nombre']} {self.usuario_actual['apellido']}",
                    motivo="Cierre regular de período")
                # Detalles para auditoria
                detalle = (f"Cierre de período:\n"
                           f"ID: {self.periodo_seleccionado}\n"
                           f"Cerrado por: {self.usuario_actual['nombre']} {self.usuario_actual['apellido']}\n"
                           f"Motivo: Cierre regular de período")

                self.db_manager.registrar_auditoria(
                    usuario=f"{self.usuario_actual['nombre']} {self.usuario_actual['apellido']}",
                    rol=f"{self.usuario_actual['rol']}",
                    accion='Cerró período',
                    tabla='periodos_nomina',
                    detalle=detalle)
                messagebox.showinfo("Éxito", "Período cerrado correctamente")
                self.cargar_periodos()
            except Exception as e:
                messagebox.showerror("Error", f"Error al cerrar el período: {str(e)}")

    def ver_historial(self):
        """Mostrar el historial del período seleccionado"""
        if not self.periodo_seleccionado:
            messagebox.showwarning("Advertencia", "Por favor seleccione un período")
            return
            
        historial = self.db_manager.obtener_historial_periodo(self.periodo_seleccionado)
        if historial:
            # Crear nueva ventana para mostrar el historial
            historial_window = tk.Toplevel(self)
            historial_window.title("Historial del Período")
            historial_window.geometry("600x400")
            
            # Crear Treeview para el historial
            tree_historial = ttk.Treeview(historial_window, columns=(
                "fecha", "estado_anterior", "estado_nuevo", "usuario", "motivo"
            ), show='headings')
            
            # Configurar columnas
            for col in tree_historial['columns']:
                tree_historial.heading(col, text=col.title())
            
            # Insertar datos
            for registro in historial:
                tree_historial.insert('', 'end', values=registro)
            
            tree_historial.pack(fill=tk.BOTH, expand=True)
        else:
            messagebox.showinfo("Información", "No hay historial para este período")

    def on_select(self, event):
        """Manejar la selección de un período"""
        selected_items = self.tree.selection()
        if selected_items:
            item = selected_items[0]
            self.periodo_seleccionado = self.tree.item(item)['values'][0]