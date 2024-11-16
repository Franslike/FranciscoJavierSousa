import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
from datetime import datetime

class ReportesForm(tk.Toplevel):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        
        # Configuración básica de la ventana
        self.title("Visor de Reportes")
        self.geometry("1000x600")
        
        # Frame principal
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame superior para filtros
        self.filtros_frame = ttk.LabelFrame(self.main_frame, text="Filtros", padding="5")
        self.filtros_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Filtro por periodo
        ttk.Label(self.filtros_frame, text="Período:").pack(side=tk.LEFT, padx=5)
        self.periodo_var = tk.StringVar()
        self.periodo_combo = ttk.Combobox(self.filtros_frame, 
                                        textvariable=self.periodo_var,
                                        width=40,
                                        state="readonly")
        self.periodo_combo.pack(side=tk.LEFT, padx=5)
        
        # Frame principal para el Treeview
        self.tree_frame = ttk.Frame(self.main_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Crear Treeview
        self.columns = ("periodo", "empleado", "cedula", "fecha_generacion", "archivo")
        self.tree = ttk.Treeview(self.tree_frame, columns=self.columns, show='headings')
        
        # Configurar columnas
        self.tree.heading("periodo", text="Período")
        self.tree.heading("empleado", text="Empleado")
        self.tree.heading("cedula", text="Cédula")
        self.tree.heading("fecha_generacion", text="Fecha Generación")
        self.tree.heading("archivo", text="Archivo")
        
        # Configurar anchos de columna
        self.tree.column("periodo", width=150)
        self.tree.column("empleado", width=200)
        self.tree.column("cedula", width=100)
        self.tree.column("fecha_generacion", width=150)
        self.tree.column("archivo", width=300)
        
        # Scrollbars
        vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid del Treeview y scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(0, weight=1)
        
        # Frame para botones
        self.botones_frame = ttk.Frame(self.main_frame)
        self.botones_frame.pack(fill=tk.X, pady=5)
        
        # Botones
        ttk.Button(self.botones_frame, text="Abrir Reporte",
                  command=self.abrir_reporte).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.botones_frame, text="Abrir Carpeta",
                  command=self.abrir_carpeta).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.botones_frame, text="Actualizar",
                  command=self.cargar_reportes).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.botones_frame, text="Cerrar",
                  command=self.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Bindings
        self.tree.bind('<Double-1>', lambda e: self.abrir_reporte())
        self.periodo_combo.bind('<<ComboboxSelected>>', lambda e: self.cargar_reportes())
        
        # Inicializar
        self.cargar_periodos()
        self.cargar_reportes()
    
    def cargar_periodos(self):
        """Cargar los períodos en el combobox"""
        periodos = self.db_manager.obtener_periodos()
        self.periodo_combo['values'] = [
            f"{p[1]} ({p[2]} - {p[3]})" for p in periodos
        ]
        if periodos:
            self.periodo_combo.set(self.periodo_combo['values'][0])
    
    def cargar_reportes(self):
        """Cargar los reportes del período seleccionado"""
        # Limpiar Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.periodo_var.get():
            return
        
        # Obtener fecha del período seleccionado
        periodo_info = self.periodo_var.get()
        fechas = periodo_info.split('(')[1].split(')')[0]
        fecha_inicio, fecha_fin = fechas.split(' - ')
        
        # Ruta base de los reportes
        ruta_reportes = f"nominas_pdf/periodo_{fecha_inicio}-{fecha_fin}"
        
        if not os.path.exists(ruta_reportes):
            return
            
        # Listar archivos en la carpeta
        for archivo in os.listdir(ruta_reportes):
            if archivo.endswith('.pdf'):
                # Obtener información del archivo
                ruta_completa = os.path.join(ruta_reportes, archivo)
                fecha_mod = datetime.fromtimestamp(os.path.getmtime(ruta_completa))
                
                # Obtener cédula del nombre del archivo
                cedula = archivo.replace('nomina_', '').replace('.pdf', '')
                
                # Obtener información del empleado
                empleado = self.db_manager.obtener_empleado_por_cedula(cedula)
                nombre_empleado = f"{empleado[1]} {empleado[2]}" if empleado else "Desconocido"
                
                # Insertar en el Treeview
                self.tree.insert('', 'end', values=(
                    periodo_info,
                    nombre_empleado,
                    cedula,
                    fecha_mod.strftime('%Y-%m-%d %H:%M'),
                    archivo
                ))
    
    def abrir_reporte(self):
        """Abrir el reporte seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un reporte")
            return
        
        # Obtener información del reporte seleccionado
        item = self.tree.item(selected[0])
        periodo = item['values'][0]
        archivo = item['values'][4]
        
        # Extraer fechas del período
        fechas = periodo.split('(')[1].split(')')[0]
        fecha_inicio, fecha_fin = fechas.split(' - ')
        
        # Construir ruta completa
        ruta_reporte = os.path.join(
            "nominas_pdf",
            f"periodo_{fecha_inicio}-{fecha_fin}",
            archivo
        )
        
        if os.path.exists(ruta_reporte):
            try:
                # Abrir el PDF con el visor predeterminado del sistema
                if os.name == 'nt':  # Windows
                    os.startfile(ruta_reporte)
                else:  # Linux/Mac
                    subprocess.run(['xdg-open', ruta_reporte])
            except Exception as e:
                messagebox.showerror("Error", f"Error al abrir el archivo: {str(e)}")
        else:
            messagebox.showerror("Error", "El archivo no existe")
    
    def abrir_carpeta(self):
        """Abrir la carpeta del período seleccionado"""
        if not self.periodo_var.get():
            messagebox.showwarning("Advertencia", "Por favor seleccione un período")
            return
        
        # Extraer fechas del período
        periodo = self.periodo_var.get()
        fechas = periodo.split('(')[1].split(')')[0]
        fecha_inicio, fecha_fin = fechas.split(' - ')
        
        # Construir ruta de la carpeta
        ruta_carpeta = os.path.join(
            "nominas_pdf",
            f"periodo_{fecha_inicio}-{fecha_fin}"
        )
        
        if os.path.exists(ruta_carpeta):
            try:
                # Abrir el explorador de archivos en la carpeta
                if os.name == 'nt':  # Windows
                    os.startfile(ruta_carpeta)
                else:  # Linux/Mac
                    subprocess.run(['xdg-open', ruta_carpeta])
            except Exception as e:
                messagebox.showerror("Error", f"Error al abrir la carpeta: {str(e)}")
        else:
            messagebox.showerror("Error", "La carpeta no existe")