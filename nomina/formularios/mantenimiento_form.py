import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
from datetime import datetime
import shutil
from util.config import DB_CONFIG

class MantenimientoForm(ttk.Frame):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.pack(fill=tk.BOTH, expand=True)
        
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
        
        # Fecha inicio
        ttk.Label(filter_frame, text="Desde:").grid(row=0, column=0, padx=5, pady=5)
        self.fecha_inicio = ttk.Entry(filter_frame)
        self.fecha_inicio.grid(row=0, column=1, padx=5, pady=5)
        
        # Fecha fin
        ttk.Label(filter_frame, text="Hasta:").grid(row=0, column=2, padx=5, pady=5)
        self.fecha_fin = ttk.Entry(filter_frame)
        self.fecha_fin.grid(row=0, column=3, padx=5, pady=5)
        
        # Usuario
        ttk.Label(filter_frame, text="Usuario:").grid(row=0, column=4, padx=5, pady=5)
        self.usuario_filter = ttk.Entry(filter_frame)
        self.usuario_filter.grid(row=0, column=5, padx=5, pady=5)
        
        # Botón buscar
        ttk.Button(filter_frame, text="Buscar",
                  command=self.buscar_logs).grid(row=0, column=6, padx=5, pady=5)
        
        # Frame para lista de logs
        list_frame = ttk.Frame(self.audit_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Crear Treeview
        self.audit_tree = ttk.Treeview(list_frame, columns=(
            "fecha", "usuario", "accion", "tabla", "detalle"
        ), show='headings')
        
        # Configurar columnas
        self.audit_tree.heading("fecha", text="Fecha")
        self.audit_tree.heading("usuario", text="Usuario")
        self.audit_tree.heading("accion", text="Acción")
        self.audit_tree.heading("tabla", text="Tabla")
        self.audit_tree.heading("detalle", text="Detalle")
        
        self.audit_tree.column("fecha", width=150)
        self.audit_tree.column("usuario", width=100)
        self.audit_tree.column("accion", width=100)
        self.audit_tree.column("tabla", width=100)
        self.audit_tree.column("detalle", width=300)
        
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
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
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
                    fecha_str = fecha.strftime('%Y-%m-%d %H:%M:%S')
                    
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

    def buscar_logs(self):
        """Buscar logs según filtros"""
        # Obtener valores de filtros
        fecha_inicio = self.fecha_inicio.get()
        fecha_fin = self.fecha_fin.get()
        usuario = self.usuario_filter.get()
        
        try:
            # Construir query base
            query = """
            SELECT a.fecha, a.usuario, a.accion, a.tabla, a.detalle
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