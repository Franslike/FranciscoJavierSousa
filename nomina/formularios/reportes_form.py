import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
from datetime import datetime
from util.ayuda import Ayuda

class ReportesForm(ttk.Frame):
    def __init__(self, parent, db_manager, usuario_actual):
        super().__init__(parent)
        self.db_manager = db_manager
        self.usuario_actual = usuario_actual
        self.sistema_ayuda = Ayuda()

        self.bind_all("<F1>", self.mostrar_ayuda)
        
        self.pack(fill=tk.BOTH, expand=True)

        alcance = self.db_manager.verificar_permiso(
            usuario_actual['id_usuario'], 
            'reportes.ver'
        )
        
        if not alcance:
            messagebox.showerror("Error", "No tienes los permisos suficientes para acceder a este módulo.")
            self.destroy()
            return
            
        self.tiene_acceso_global = alcance == 'GLOBAL'
        
        # Frame principal
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Titulo
        ttk.Label(self.main_frame, text="Reportes", font=('Helvetica', 12, 'bold')).pack(anchor='w', pady=(0,5))
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Pestaña para recibos de nómina
        self.recibos_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.recibos_frame, text="Recibos de Nómina")
        self.setup_recibos_frame()

        # Nueva pestaña para reportes analíticos
        if self.tiene_acceso_global:
            self.reportes_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.reportes_frame, text="Reportes Analíticos")
            self.setup_reportes_frame()

    def setup_recibos_frame(self):
        """Configurar la pestaña de recibos de nómina"""
        # Frame superior para filtros
        self.filtros_frame = ttk.LabelFrame(self.recibos_frame, text="Filtros", padding="5")
        self.filtros_frame.pack(fill=tk.X, padx=5, pady=5)

        # Tipo de reporte
        ttk.Label(self.filtros_frame, text="Tipo de Reporte:").pack(side=tk.LEFT, padx=5)
        self.tipo_reporte_var = tk.StringVar(value="Recibos de Nómina")
        self.tipo_reporte_combo = ttk.Combobox(self.filtros_frame, 
                                            textvariable=self.tipo_reporte_var,
                                            values=["Recibos de Nómina", "Deducciones"],
                                            state="readonly" if self.tiene_acceso_global else "disabled",
                                            width=25)
        self.tipo_reporte_combo.pack(side=tk.LEFT, padx=5)
        
        # Filtro por periodo
        self.periodo_label = ttk.Label(self.filtros_frame, text="Período:")
        self.periodo_label.pack(side=tk.LEFT, padx=5)
        self.periodo_var = tk.StringVar()
        self.periodo_combo = ttk.Combobox(self.filtros_frame, 
                                        textvariable=self.periodo_var,
                                        width=40,
                                        state="readonly")
        self.periodo_combo.pack(side=tk.LEFT, padx=5)
        
        # Frame principal para el Treeview
        self.tree_frame = ttk.Frame(self.recibos_frame)
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
        self.botones_frame = ttk.Frame(self.recibos_frame)
        self.botones_frame.pack(fill=tk.X, pady=5)
        
        # Botones
        ttk.Button(self.botones_frame, text="Abrir Reporte",
                  command=self.abrir_reporte).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.botones_frame, text="Abrir Carpeta",
                  command=self.abrir_carpeta).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.botones_frame, text="Actualizar",
                  command=self.cargar_reportes).pack(side=tk.LEFT, padx=5)
        
        # Configurar permisos
        if not self.tiene_acceso_global:
            for button in self.botones_frame.winfo_children():
                if button['text'] == "Abrir Carpeta":
                    button.configure(state='disabled')
        
        # Bindings
        self.tree.bind('<Double-1>', lambda e: self.abrir_reporte())
        self.periodo_combo.bind('<<ComboboxSelected>>', lambda e: self.cargar_reportes())
        
        # Inicializar
        self.cargar_periodos()
        self.cargar_reportes()

        # Agregar binding al combobox de tipo de reporte
        self.tipo_reporte_combo.bind('<<ComboboxSelected>>', self.cambiar_tipo_reporte)

    def setup_reportes_frame(self):
        """Configurar la nueva pestaña de reportes analíticos"""
        from reportes.reportes_deducciones_form import ReporteDeducciones
        ReporteDeducciones(self.reportes_frame, self.db_manager)

    def mostrar_ayuda(self, event=None):
        """Muestra la ayuda contextual del módulo de empleados"""
        self.sistema_ayuda.mostrar_ayuda('reportes')

    def cambiar_tipo_reporte(self, event=None):
        tipo = self.tipo_reporte_var.get()
        if tipo == "Deducciones":
            self.periodo_label.pack_forget()
            self.periodo_combo.pack_forget()
            
            # Actualizar columnas para mostrar información más relevante
            self.tree['columns'] = ("tipo_deduccion", "fecha_generacion", "archivo", "ruta")
            self.tree.heading("tipo_deduccion", text="Tipo de Deducción")
            self.tree.heading("fecha_generacion", text="Fecha Generación")
            self.tree.heading("archivo", text="Archivo")
            self.tree.heading("ruta", text="Ubicación")

            self.tree.column("tipo_deduccion", width=150)
            self.tree.column("fecha_generacion", width=150)
            self.tree.column("archivo", width=200)
            self.tree.column("ruta", width=300)
        else:
            # Mostrar filtro de período si no está visible
            self.periodo_label.pack(side=tk.LEFT, padx=5)  # Mostrar el label
            self.periodo_combo.pack(side=tk.LEFT, padx=5)
            
            # Restaurar columnas originales
            self.tree['columns'] = self.columns
            for col in self.columns:
                self.tree.heading(col, text=col.replace("_", " ").title())
        
        # Recargar reportes
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
        """Cargar reportes según el tipo seleccionado"""
        # Limpiar Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.periodo_var.get():
            return
        
        # Obtener tipo de reporte seleccionado
        tipo_reporte = self.tipo_reporte_var.get()
        
        if tipo_reporte == "Recibos de Nómina":
            self.cargar_recibos_nomina()
        elif tipo_reporte == "Deducciones":
            self.cargar_reporte_deducciones()

    def cargar_recibos_nomina(self):
        """Cargar recibos de nómina del período seleccionado"""
        periodo_info = self.periodo_var.get()
        fechas = periodo_info.split('(')[1].split(')')[0]
        fecha_inicio, fecha_fin = fechas.split(' - ')
        
        ruta_reportes = f"nominas_pdf/periodo_{fecha_inicio}-{fecha_fin}"
        
        if not os.path.exists(ruta_reportes):
            return
            
        for archivo in os.listdir(ruta_reportes):
            if archivo.endswith('.pdf'):
                ruta_completa = os.path.join(ruta_reportes, archivo)
                fecha_mod = datetime.fromtimestamp(os.path.getmtime(ruta_completa))
                
                cedula = archivo.replace('recibo de pago_', '').replace('.pdf', '')
                
                if not self.tiene_acceso_global:
                    query = "SELECT cedula_identidad FROM empleados WHERE id_empleado = %s"
                    empleado = self.db_manager.ejecutar_query(query, (self.usuario_actual['id_empleado'],), fetchone=True)
                    if cedula != empleado[0]:
                        continue
                
                empleado = self.db_manager.obtener_empleado_por_cedula(cedula)
                nombre_empleado = f"{empleado[1]} {empleado[2]}" if empleado else "Desconocido"
                
                self.tree.insert('', 'end', values=(
                    periodo_info,
                    nombre_empleado,
                    cedula,
                    fecha_mod.strftime('%d-%m-%Y %H:%M'),
                    archivo
                ))
    
    def cargar_reporte_deducciones(self):
        output_folder = os.path.join("reportes", "deducciones")
        
        if not os.path.exists(output_folder):
            return
            
        for archivo in os.listdir(output_folder):
            if archivo.startswith('reporte_deduccion_') and archivo.endswith('.pdf'):
                ruta_completa = os.path.join(output_folder, archivo)
                fecha_mod = datetime.fromtimestamp(os.path.getmtime(ruta_completa))
                
                # Extraer tipo de deducción del nombre del archivo
                partes = archivo.replace('reporte_deduccion_', '').replace('.pdf', '').split('_')
                tipo_deduccion = partes[0].replace('_', ' ').title()
                
                self.tree.insert('', 'end', values=(
                    tipo_deduccion,
                    fecha_mod.strftime('%d-%m-%Y %H:%M'),
                    archivo,
                    ruta_completa
                ))

    def abrir_reporte(self):
        """Abrir el reporte seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un reporte")
            return
        
        item = self.tree.item(selected[0])
        tipo_reporte = self.tipo_reporte_var.get()
        
        if tipo_reporte == "Deducciones":
            ruta_reporte = item['values'][3]  # La ruta completa está en el índice 3
            detalle = (f"Acceso a reporte de deducciones:\n"
                    f"Tipo: {item['values'][0]}\n"
                    f"Fecha: {item['values'][1]}\n"
                    f"Archivo: {item['values'][2]}")
        else:
            # Lógica existente para recibos de nómina
            periodo = item['values'][0]
            archivo = item['values'][4]
            fechas = periodo.split('(')[1].split(')')[0]
            fecha_inicio, fecha_fin = fechas.split(' - ')
            ruta_reporte = os.path.join(
                "nominas_pdf",
                f"periodo_{fecha_inicio}-{fecha_fin}",
                archivo
            )
            detalle = (f"Acceso a reporte de nómina:\n"
                    f"Empleado: {item['values'][1]}\n"
                    f"Cédula: {item['values'][2]}\n"
                    f"Período: {item['values'][0]}")

        if os.path.exists(ruta_reporte):
            try:
                if os.name == 'nt':
                    os.startfile(ruta_reporte)
                else:
                    subprocess.run(['xdg-open', ruta_reporte])
                    
                self.db_manager.registrar_auditoria(
                    usuario=f"{self.usuario_actual['nombre']} {self.usuario_actual['apellido']}",
                    rol=f"{self.usuario_actual['rol']}",
                    accion='Accesó a reporte',
                    tabla='reportes',
                    detalle=detalle
                )
            except Exception as e:
                messagebox.showerror("Error", f"Error al abrir el archivo: {str(e)}")
        else:
            messagebox.showerror("Error", "El archivo no existe")
    
    def abrir_carpeta(self):
        """Abrir la carpeta del período seleccionado"""
        tipo_reporte = self.tipo_reporte_var.get()
        
        if tipo_reporte == "Deducciones":
            ruta_carpeta = os.path.join("reportes", "deducciones")
            detalle = "Acceso a carpeta de reportes de deducciones"
        else:
            if not self.periodo_var.get():
                messagebox.showwarning("Advertencia", "Por favor seleccione un período")
                return
            
            periodo = self.periodo_var.get()
            fechas = periodo.split('(')[1].split(')')[0]
            fecha_inicio, fecha_fin = fechas.split(' - ')
            
            ruta_carpeta = os.path.join(
                "nominas_pdf",
                f"periodo_{fecha_inicio}-{fecha_fin}"
            )
            detalle = f"Acceso a carpeta de reportes del período: {periodo}"

        if os.path.exists(ruta_carpeta):
            try:
                if os.name == 'nt':
                    os.startfile(ruta_carpeta)
                else:
                    subprocess.run(['xdg-open', ruta_carpeta])
                    
                self.db_manager.registrar_auditoria(
                    usuario=f"{self.usuario_actual['nombre']} {self.usuario_actual['apellido']}",
                    rol=f"{self.usuario_actual['rol']}",
                    accion='Accesó a carpeta',
                    tabla='reportes',
                    detalle=detalle
                )
            except Exception as e:
                messagebox.showerror("Error", f"Error al abrir la carpeta: {str(e)}")
        else:
            messagebox.showerror("Error", "La carpeta no existe")