import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import subprocess
import os
from datetime import datetime
import shutil
from util.config import DB_CONFIG
from util.ayuda import Ayuda

class MantenimientoForm(ttk.Frame):
    def __init__(self, parent, db_manager, usuario_actual):
        super().__init__(parent)
        self.usuario_actual = usuario_actual
        self.db_manager = db_manager
        self.sistema_ayuda = Ayuda()

        self.bind_all("<F1>", self.mostrar_ayuda)

        self.pack(fill=tk.BOTH, expand=True)

        # Verificar permisos
        alcance = self.db_manager.verificar_permiso(
            usuario_actual['id_usuario'], 
            'mantenimiento.gestion'
        )

        if not alcance or alcance != 'GLOBAL':
            messagebox.showerror("Error", "No tienes los permisos suficientes para ingresar a este módulo.")
            self.destroy()
            return
        
        # Crear directorio de respaldos si no existe
        self.backup_dir = "backups"
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

        # Frame principal
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Titulo
        ttk.Label(self.main_frame, text="Mantenimiento", font=('Helvetica', 12, 'bold')).pack(anchor='w', pady=(0,5))
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Crear pestañas
        self.backup_frame = ttk.Frame(self.notebook)
        self.audit_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.backup_frame, text="Respaldo y Restauración")
        self.notebook.add(self.audit_frame, text="Auditoría")
        
        self.setup_backup_frame()
        self.setup_audit_frame()

    def mostrar_ayuda(self, event=None):
        """Muestra la ayuda contextual del módulo de empleados"""
        self.sistema_ayuda.mostrar_ayuda('mantenimiento')
        
    def setup_backup_frame(self):
        """Configurar pestaña de respaldo y restauración"""
        # Frame superior para acciones
        action_frame = ttk.Frame(self.backup_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="Crear Respaldo",
                  command=self.create_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Restaurar Respaldo",
                  command=self.restore_backup).pack(side=tk.LEFT, padx=5)
        
        # Frame para lista de respaldos
        list_frame = ttk.LabelFrame(self.backup_frame, text="Respaldos Disponibles")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Crear Treeview
        self.backup_tree = ttk.Treeview(list_frame, columns=(
            "fecha", "tamaño", "ruta"
        ), show='headings')
        
        # Configurar columnas
        self.backup_tree.heading("fecha", text="Fecha")
        self.backup_tree.heading("tamaño", text="Tamaño")
        self.backup_tree.heading("ruta", text="Ubicación")
        
        self.backup_tree.column("fecha", width=150)
        self.backup_tree.column("tamaño", width=100)
        self.backup_tree.column("ruta", width=300)
        
        # Scrollbars
        scrolly = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                              command=self.backup_tree.yview)
        scrollx = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL,
                              command=self.backup_tree.xview)
        self.backup_tree.configure(yscrollcommand=scrolly.set,
                                 xscrollcommand=scrollx.set)
        
        # Grid
        self.backup_tree.grid(row=0, column=0, sticky='nsew')
        scrolly.grid(row=0, column=1, sticky='ns')
        scrollx.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        self.cargar_respaldos()

    def setup_audit_frame(self):
        """Configurar pestaña de auditoría"""
        # Frame de filtros
        filter_frame = ttk.LabelFrame(self.audit_frame, text="Filtros")
        filter_frame.pack(fill=tk.X, pady=10)
        
        # Frame para búsqueda y fechas
        search_frame = ttk.Frame(filter_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Fechas con DateEntry
        ttk.Label(search_frame, text="Desde:").pack(side=tk.LEFT, padx=5)
        self.fecha_inicio = DateEntry(search_frame, width=12, background='darkblue',
                                    foreground='white', borderwidth=2,
                                    date_pattern='dd/mm/yyyy')
        self.fecha_inicio.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(search_frame, text="Hasta:").pack(side=tk.LEFT, padx=5)
        self.fecha_fin = DateEntry(search_frame, width=12, background='darkblue',
                                foreground='white', borderwidth=2,
                                date_pattern='dd/mm/yyyy')
        self.fecha_fin.pack(side=tk.LEFT, padx=5)

        # Campo de búsqueda general
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        # Vincular eventos de búsqueda
        self.search_var.trace('w', self.filtrar_registros)
        self.fecha_inicio.bind('<<DateEntrySelected>>', self.filtrar_registros)
        self.fecha_fin.bind('<<DateEntrySelected>>', self.filtrar_registros)

        # Frame para lista de logs
        list_frame = ttk.Frame(self.audit_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Frame para paginación (arriba del Treeview)
        pagination_frame = ttk.Frame(self.audit_frame)
        pagination_frame.pack(fill=tk.X, pady=5)
        
        # Crear Treeview
        self.audit_tree = ttk.Treeview(list_frame, columns=(
            "fecha", "usuario", "rol", "accion", "tabla", "detalle"
        ), show='headings')
        
        # Configurar columnas
        self.audit_tree.heading("fecha", text="Fecha")
        self.audit_tree.heading("usuario", text="Usuario")
        self.audit_tree.heading("rol", text="Rol")
        self.audit_tree.heading("accion", text="Acción")
        self.audit_tree.heading("tabla", text="Tabla")
        self.audit_tree.heading("detalle", text="Detalle")
        
        self.audit_tree.column("fecha", width=150)
        self.audit_tree.column("usuario", width=100)
        self.audit_tree.column("rol", width=100)
        self.audit_tree.column("accion", width=100)
        self.audit_tree.column("tabla", width=100)
        self.audit_tree.column("detalle", width=300)

        self.audit_tree.bind('<Double-1>', self.ver_detalle_auditoria)
        
        # Scrollbars
        scrolly = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                              command=self.audit_tree.yview)
        scrollx = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL,
                              command=self.audit_tree.xview)
        self.audit_tree.configure(yscrollcommand=scrolly.set,
                                xscrollcommand=scrollx.set)
        
        # Grid
        self.audit_tree.grid(row=0, column=0, sticky='nsew')
        scrolly.grid(row=0, column=1, sticky='ns')
        scrollx.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)

        # Registros por página
        ttk.Label(pagination_frame, text="Registros por página:").pack(side=tk.LEFT, padx=5)
        self.registros_pagina = tk.StringVar(value="25")
        self.combo_registros = ttk.Combobox(
            pagination_frame, 
            textvariable=self.registros_pagina,
            values=["10", "25", "50", "100"],
            state="readonly",
            width=5
        )
        self.combo_registros.pack(side=tk.LEFT, padx=5)
        self.combo_registros.bind('<<ComboboxSelected>>', self.cambiar_registros_pagina)

        # Botones de navegación
        self.btn_primera = ttk.Button(pagination_frame, text="<<", command=self.primera_pagina)
        self.btn_anterior = ttk.Button(pagination_frame, text="<", command=self.pagina_anterior)
        self.lbl_pagina = ttk.Label(pagination_frame, text="Página 1 de 1")
        self.btn_siguiente = ttk.Button(pagination_frame, text=">", command=self.pagina_siguiente)
        self.btn_ultima = ttk.Button(pagination_frame, text=">>", command=self.ultima_pagina)

        self.btn_primera.pack(side=tk.LEFT, padx=2)
        self.btn_anterior.pack(side=tk.LEFT, padx=2)
        self.lbl_pagina.pack(side=tk.LEFT, padx=10)
        self.btn_siguiente.pack(side=tk.LEFT, padx=2)
        self.btn_ultima.pack(side=tk.LEFT, padx=2)

        # Variables de control para paginación
        self.pagina_actual = 1
        self.total_registros = 0
        self.total_paginas = 1

        self.cargar_logs()

    def ver_detalle_auditoria(self, event=None):
        """Mostrar ventana con detalles del registro de auditoría seleccionado"""
        selected = self.audit_tree.selection()
        if not selected:
            return
            
        item = self.audit_tree.item(selected[0])
        valores = list(item['values'])
        valores[4] = item['tags'][0]
        
        DetalleAuditoriaWindow(self, valores)

    def filtrar_registros(self, *args):
        """Filtrar registros de auditoría según texto de búsqueda y fechas"""
        try:
            # Obtener fechas y texto de búsqueda
            fecha_inicio = self.fecha_inicio.get_date()
            fecha_fin = self.fecha_fin.get_date()
            texto = self.search_var.get().lower()
            
            # Construir query base
            query = """
            SELECT DATE_FORMAT(a.fecha, '%d-%m-%Y %H:%i') as fecha, 
                a.usuario, a.accion, a.tabla, a.detalle
            FROM auditoria a
            WHERE a.fecha BETWEEN %s AND DATE_ADD(%s, INTERVAL 1 DAY)
            """
            params = [fecha_inicio, fecha_fin]
            
            # Agregar filtro de búsqueda si hay texto
            if texto:
                query += """ 
                AND (
                    LOWER(a.usuario) LIKE %s OR
                    LOWER(a.accion) LIKE %s OR
                    LOWER(a.tabla) LIKE %s OR
                    LOWER(a.detalle) LIKE %s
                )
                """
                params.extend([f"%{texto}%"] * 4)  # Agregar el parámetro 4 veces para cada campo
            
            # Ordenar por fecha descendente
            query += " ORDER BY a.fecha DESC"
            
            # Ejecutar consulta
            registros = self.db_manager.ejecutar_query(query, params)
            
            # Limpiar y actualizar Treeview
            for item in self.audit_tree.get_children():
                self.audit_tree.delete(item)
                
            for registro in registros:
                valores = list(registro)
                valores[4] = self.formatear_detalle(valores[4])
                self.audit_tree.insert('', 'end', values=valores)
                
        except Exception as e:
            print(f"Error al filtrar registros: {str(e)}")

    def formatear_detalle(self, detalle):
        """
        Formatea el detalle para mostrar solo la primera línea con tres puntos
        """
        if not detalle:  # Si el detalle está vacío
            return ""
            
        # Dividir por saltos de línea y tomar la primera línea
        primera_linea = detalle.split('\n')[0].strip()
        
        # Si hay más líneas, agregar ...
        if '\n' in detalle:
            primera_linea += "..."
            
        return primera_linea

    def create_backup(self):
        try:
            mysqldump_path = "C:/Program Files/MySQL/MySQL Server 8.3/bin/mysqldump"
            command = [
                mysqldump_path,
                f'--host={DB_CONFIG["host"]}',
                f'--user={DB_CONFIG["user"]}',
                f'--password={DB_CONFIG["password"]}',
                DB_CONFIG["database"]
            ]
            
            timestamp = datetime.now().strftime('%d%m%Y_%H%M%S')
            filename = f"backup_{timestamp}.sql"
            backup_path = os.path.join(self.backup_dir, filename)
            
            with open(backup_path, 'w') as f:
                subprocess.run(command, stdout=f, check=True)
                
            messagebox.showinfo("Éxito", "Respaldo creado correctamente")
            self.cargar_respaldos()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear respaldo: {str(e)}")

    def restore_backup(self):
        try:
            selected = self.backup_tree.selection()
            if not selected:
                messagebox.showwarning("Advertencia", "Por favor seleccione un respaldo")
                return
                
            if messagebox.askyesno("Confirmar", "¿Está seguro de restaurar este respaldo? Esto sobrescribirá todos los datos actuales."):
                backup_path = self.backup_tree.item(selected[0])['values'][2]
                mysql_path = "C:/Program Files/MySQL/MySQL Server 8.3/bin/mysql"
                
                command = [
                    mysql_path,
                    f'--host={DB_CONFIG["host"]}',
                    f'--user={DB_CONFIG["user"]}',
                    f'--password={DB_CONFIG["password"]}',
                    DB_CONFIG["database"]
                ]
                
                with open(backup_path, 'r') as f:
                    subprocess.run(command, stdin=f, check=True)
                
                messagebox.showinfo("Éxito", "Base de datos restaurada correctamente")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al restaurar: {str(e)}")


    def cargar_respaldos(self):
        """Cargar lista de respaldos disponibles"""
        # Limpiar treeview
        for item in self.backup_tree.get_children():
            self.backup_tree.delete(item)
            
        # Listar archivos en directorio de respaldos
        if os.path.exists(self.backup_dir):
            for file in os.listdir(self.backup_dir):
                if file.endswith('.sql'):
                    path = os.path.join(self.backup_dir, file)
                    stats = os.stat(path)
                    
                    # Convertir timestamp a fecha legible
                    fecha = datetime.fromtimestamp(stats.st_mtime)
                    fecha_str = fecha.strftime('%d-%m-%Y %H:%M:%S')
                    
                    # Convertir tamaño a formato legible
                    size = stats.st_size
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024**2:
                        size_str = f"{size/1024:.1f} KB"
                    else:
                        size_str = f"{size/1024**2:.1f} MB"
                    
                    self.backup_tree.insert('', 'end', values=(
                        fecha_str,
                        size_str,
                        path
                    ))


    def cargar_logs(self):
        try:
            # Query para contar registros
            query_count = "SELECT COUNT(*) FROM auditoria"
            self.total_registros = self.db_manager.ejecutar_query(query_count, fetchone=True)[0]
            
            registros_por_pagina = int(self.registros_pagina.get())
            self.total_paginas = (self.total_registros + registros_por_pagina - 1) // registros_por_pagina
            
            if self.pagina_actual > self.total_paginas:
                self.pagina_actual = self.total_paginas
            if self.pagina_actual < 1:
                self.pagina_actual = 1

            offset = (self.pagina_actual - 1) * registros_por_pagina

            # Query actualizado para incluir el rol
            query = f"""
            SELECT DATE_FORMAT(a.fecha, '%d-%m-%Y %H:%i') as fecha, 
                a.usuario, 
                COALESCE(a.rol, 'No especificado') as rol,
                a.accion, 
                a.tabla, 
                a.detalle
            FROM auditoria a
            ORDER BY a.fecha DESC
            LIMIT {registros_por_pagina} OFFSET {offset}
            """
            
            logs = self.db_manager.ejecutar_query(query)
            self.actualizar_treeview(logs)
            self.actualizar_controles_paginacion()
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar registros: {str(e)}")

    def buscar_logs(self):
        """Buscar logs según filtros"""
        # Obtener valores de filtros
        fecha_inicio = self.fecha_inicio.get()
        fecha_fin = self.fecha_fin.get()
        usuario = self.usuario_filter.get()
        
        try:
            # Construir query base
            query = """
            SELECT DATE_FORMAT (a.fecha, '%d-%m-%Y %H:%i') as fecha, a.usuario, a.accion, a.tabla, a.detalle
            FROM auditoria a
            WHERE 1=1
            """
            params = []
            
            # Agregar filtros si existen
            if fecha_inicio:
                query += " AND a.fecha >= %s"
                params.append(fecha_inicio)
            if fecha_fin:
                query += " AND a.fecha <= %s"
                params.append(fecha_fin)
            if usuario:
                query += " AND a.usuario LIKE %s"
                params.append(f"%{usuario}%")
                
            # Ordenar por fecha
            query += " ORDER BY a.fecha DESC"
            
            # Ejecutar query
            logs = self.db_manager.ejecutar_query(query, params)
            
            # Limpiar treeview
            for item in self.audit_tree.get_children():
                self.audit_tree.delete(item)
                
            # Insertar resultados
            for log in logs:
                self.audit_tree.insert('', 'end', values=log)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar logs: {str(e)}")


    def actualizar_controles_paginacion(self):
        """Actualizar estado de los botones y etiqueta de paginación"""
        self.lbl_pagina.configure(text=f"Página {self.pagina_actual} de {self.total_paginas}")
        
        # Habilitar/deshabilitar botones según corresponda
        self.btn_primera.configure(state='normal' if self.pagina_actual > 1 else 'disabled')
        self.btn_anterior.configure(state='normal' if self.pagina_actual > 1 else 'disabled')
        self.btn_siguiente.configure(state='normal' if self.pagina_actual < self.total_paginas else 'disabled')
        self.btn_ultima.configure(state='normal' if self.pagina_actual < self.total_paginas else 'disabled')

    def primera_pagina(self):
        self.pagina_actual = 1
        self.cargar_logs()

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.cargar_logs()

    def pagina_siguiente(self):
        if self.pagina_actual < self.total_paginas:
            self.pagina_actual += 1
            self.cargar_logs()

    def ultima_pagina(self):
        self.pagina_actual = self.total_paginas
        self.cargar_logs()

    def cambiar_registros_pagina(self, event):
        """Cuando se cambia el número de registros por página"""
        self.pagina_actual = 1  # Volver a la primera página
        self.cargar_logs()

    def actualizar_treeview(self, registros):
        """
        Actualiza el Treeview con los registros proporcionados
        
        Args:
            registros: Lista de registros a mostrar en el Treeview
        """
        # Limpiar treeview actual
        for item in self.audit_tree.get_children():
            self.audit_tree.delete(item)
            
        # Insertar nuevos registros
        for registro in registros:
            valores = list(registro)
            detalle_completo = valores[5]  # Guardamos el detalle completo
            valores[5] = self.formatear_detalle(valores[5])  # Detalle formateado para mostrar
            
            # Insertamos con el detalle formateado y guardamos el detalle completo como tag
            self.audit_tree.insert('', 'end', values=valores, tags=(detalle_completo,))

class DetalleAuditoriaWindow(tk.Toplevel):
    """Ventana para mostrar detalles de un registro de auditoría"""
    def __init__(self, parent, valores):
        super().__init__(parent)
        
        # Configuración básica de la ventana
        self.title("Detalle de Auditoría")
        self.geometry("600x400")
        self.configure(bg='white')
        
        # Hacer la ventana modal
        self.transient(parent)
        self.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear campos de detalle
        campos = [
            ("Fecha:", valores[0]),
            ("Usuario:", valores[1]),
            ("Acción:", valores[2]),
            ("Tabla:", valores[3])
        ]
        
        # Mostrar campos en grid
        for i, (label, value) in enumerate(campos):
            ttk.Label(main_frame, text=label, 
                     font=('Helvetica', 10, 'bold')).grid(
                row=i, column=0, sticky='w', padx=5, pady=5)
            ttk.Label(main_frame, text=value).grid(
                row=i, column=1, sticky='w', padx=5, pady=5)
        
        # Frame para el detalle con scroll
        detalle_frame = ttk.LabelFrame(main_frame, text="Detalle", padding="10")
        detalle_frame.grid(row=len(campos), column=0, columnspan=2, 
                         sticky='nsew', pady=(10,0))
        
        # Text widget para mostrar el detalle
        self.detalle_text = tk.Text(detalle_frame, wrap=tk.WORD, 
                                  width=50, height=10)
        self.detalle_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar para el detalle
        scrollbar = ttk.Scrollbar(detalle_frame, orient="vertical", 
                                command=self.detalle_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.detalle_text.configure(yscrollcommand=scrollbar.set)
        
        # Insertar detalle
        self.detalle_text.insert('1.0', valores[4])
        self.detalle_text.configure(state='disabled')
        
        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", 
                  command=self.destroy).grid(
            row=len(campos)+1, column=0, columnspan=2, pady=20)
        
        # Configurar grid weights
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(len(campos), weight=1)
        
        # Centrar la ventana
        self.center_window()
    
    def center_window(self):
        """Centrar la ventana en la pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')