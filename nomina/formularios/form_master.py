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
        empleados_menu.add_command(label="Gestionar Empleados", command=self.gestionar_empleados)
        empleados_menu.add_command(label="Administrar NFC", command=self.administrar_nfc)
        
        # Menú Nómina
        nomina_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Nómina", menu=nomina_menu)
        nomina_menu.add_command(label="Generar Prenómina", command=self.ver_prenominas)
        nomina_menu.add_command(label="Control de Asistencias", command=self.ver_asistencias)
        # nomina_menu.add_command(label="Editar Prenómina", command=self.editar_prenomina)
        # nomina_menu.add_command(label="Generar Nómina", command=self.generar_nomina)        

        #Menú periodos
        periodos_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Periodos", menu=periodos_menu)
        periodos_menu.add_command(label="Crear Periodo", command=self.crear_periodo)
        periodos_menu.add_command(label="Cerrar Periodo", command=self.cerrar_periodo)
        periodos_menu.add_command(label="Ver Periodos", command=self.ver_periodos)

        # Menú Reportes
        reportes_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reportes", menu=reportes_menu)
        reportes_menu.add_command(label="Ver Reporte de Nómina", command=self.ver_reportes_nomina)
        reportes_menu.add_command(label="Ver Reporte de Asistencia", command=self.ver_reporte_asistencia)

        # Menú Prestamos
        menubar.add_command(label="Prestamos", command=self.ver_prestamos)
        
        # Menú Salir
        menubar.add_command(label="Salir", command=self.confirmar_salir)

    def gestionar_empleados(self):
        """Mostrar ventana de empleados"""
        try:
            from formularios.empleados_form import EmpleadosForm
            EmpleadosForm(self, self.db_manager)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir el formulario de empleados: {str(e)}")

    def administrar_nfc(self):
        """Mostrar ventana de administración de tarjetas NFC"""
        try:
            from formularios.nfc_form import NfcForm
            NfcForm(self, self.db_manager)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir el formulario de tarjetas NFC: {str(e)}")

    def ver_asistencias(self):
        """Ver el formulario de control de asistencias"""
        try:
            from formularios.asistencias_form import AsistenciasForm
            AsistenciasForm(self, self.db_manager)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir el formulario de asistencias: {str(e)}")
    
    def ver_prenominas(self):
        """Mostrar el formulario de prenóminas"""
        try:
            from formularios.prenomina_form import PrenominaForm
            PrenominaForm(self, self.db_manager)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir el formulario de prenóminas: {str(e)}")
    
    def ver_reportes_nomina(self):
        try:
            from formularios.reportes_form import ReportesForm
            ReportesForm(self, self.db_manager)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir el formulario de reportes: {str(e)}")

    def ver_reporte_asistencia(self):
        # Aquí irá la lógica para mostrar los reportes de asistencia
        messagebox.showinfo("Reporte de Asistencia", "Reporte de asistencia generado")

    def confirmar_salir(self):
        if messagebox.askokcancel("Salir", "¿Estás seguro que deseas salir?"):
            self.destroy()
    
    def crear_periodo(self):
        """Abrir el formulario de creación de períodos"""
        try:
            # Importamos aquí para evitar problemas de importación circular
            from formularios.periodo_nomina_form import PeriodoNominaForm
            PeriodoNominaForm(self, self.db_manager)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir el formulario de períodos: {str(e)}")

    def cerrar_periodo(self):
        """Abrir ventana para cerrar un período existente"""
        form = tk.Toplevel(self)
        form.title("Cerrar Período de Nómina")
        form.geometry("500x300")
        
        # Frame principal
        main_frame = ttk.Frame(form, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Obtener períodos abiertos
        periodos = self.db_manager.obtener_periodos()
        periodos_abiertos = [p for p in periodos if p[4] == 'abierto']  # p[4] es el estado
        
        if not periodos_abiertos:
            messagebox.showinfo("Información", "No hay períodos abiertos para cerrar")
            form.destroy()
            return
        
        # Combobox para seleccionar período
        ttk.Label(main_frame, text="Seleccione el período a cerrar:").pack(pady=5)
        periodo_var = tk.StringVar()
        combo_periodos = ttk.Combobox(main_frame, 
                                    textvariable=periodo_var,
                                    state="readonly")
        combo_periodos['values'] = [f"ID: {p[0]} - {p[1]} ({p[2]} - {p[3]})" 
                                for p in periodos_abiertos]
        combo_periodos.pack(pady=5)
        
        # Campo para motivo
        ttk.Label(main_frame, text="Motivo del cierre:").pack(pady=5)
        motivo_text = tk.Text(main_frame, height=4)
        motivo_text.pack(pady=5)
        
        def confirmar_cierre():
            if not periodo_var.get():
                messagebox.showwarning("Advertencia", "Por favor seleccione un período")
                return
                
            if not motivo_text.get("1.0", tk.END).strip():
                messagebox.showwarning("Advertencia", "Por favor ingrese el motivo del cierre")
                return
                
            if messagebox.askyesno("Confirmar", "¿Está seguro de cerrar este período?"):
                try:
                    # Obtener ID del período seleccionado
                    id_periodo = int(periodo_var.get().split('-')[0].replace("ID:", "").strip())
                    
                    self.db_manager.cerrar_periodo(
                        id_periodo,
                        "admin",  # Debería ser el usuario actual
                        motivo_text.get("1.0", tk.END).strip()
                    )
                    
                    messagebox.showinfo("Éxito", "Período cerrado correctamente")
                    form.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Error al cerrar el período: {str(e)}")
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Cerrar Período",
                command=confirmar_cierre).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar",
                command=form.destroy).pack(side=tk.LEFT, padx=5)

    def ver_periodos(self):
        """Mostrar lista de todos los períodos"""
        # Crear ventana
        periodos_window = tk.Toplevel(self)
        periodos_window.title("Períodos de Nómina")
        periodos_window.geometry("800x600")
        
        # Frame principal
        main_frame = ttk.Frame(periodos_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear Treeview
        tree = ttk.Treeview(main_frame, columns=(
            "id", "tipo", "fecha_inicio", "fecha_fin", "estado", 
            "creado_por", "fecha_creacion", "cerrado_por", "fecha_cierre"
        ), show='headings')
        
        # Configurar columnas
        columns_config = {
            "id": ("ID", 50),
            "tipo": ("Tipo", 100),
            "fecha_inicio": ("Fecha Inicio", 100),
            "fecha_fin": ("Fecha Fin", 100),
            "estado": ("Estado", 80),
            "creado_por": ("Creado Por", 100),
            "fecha_creacion": ("Fecha Creación", 120),
            "cerrado_por": ("Cerrado Por", 100),
            "fecha_cierre": ("Fecha Cierre", 120)
        }
        
        for col, (heading, width) in columns_config.items():
            tree.heading(col, text=heading)
            tree.column(col, width=width)
        
        # Scrollbars
        vsb = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(main_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Cargar datos
        periodos = self.db_manager.obtener_periodos()
        for periodo in periodos:
            tree.insert('', 'end', values=periodo)
        
        # Frame para botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Botones
        ttk.Button(button_frame, text="Ver Historial",
                command=lambda: self.ver_historial_periodo(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar",
                command=lambda: self.actualizar_lista_periodos(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cerrar",
                command=periodos_window.destroy).pack(side=tk.LEFT, padx=5)

    def ver_historial_periodo(self, tree):
        """Ver historial de un período seleccionado"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un período")
            return
            
        periodo_id = tree.item(selected[0])['values'][0]
        historial = self.db_manager.obtener_historial_periodo(periodo_id)
        
        if not historial:
            messagebox.showinfo("Información", "No hay historial para este período")
            return
        
        # Crear ventana para el historial
        historial_window = tk.Toplevel(self)
        historial_window.title(f"Historial del Período {periodo_id}")
        historial_window.geometry("600x400")
        
        # Crear Treeview para el historial
        tree_hist = ttk.Treeview(historial_window, columns=(
            "fecha", "estado_anterior", "estado_nuevo", "usuario", "motivo"
        ), show='headings')
        
        # Configurar columnas
        for col in ["fecha", "estado_anterior", "estado_nuevo", "usuario", "motivo"]:
            tree_hist.heading(col, text=col.replace("_", " ").title())
        
        # Insertar datos
        for registro in historial:
            tree_hist.insert('', 'end', values=registro)
        
        tree_hist.pack(fill=tk.BOTH, expand=True)

    def actualizar_lista_periodos(self, tree):
        """Actualizar la lista de períodos en el Treeview"""
        # Limpiar árbol
        for item in tree.get_children():
            tree.delete(item)
        
        # Recargar datos
        periodos = self.db_manager.obtener_periodos()
        for periodo in periodos:
            tree.insert('', 'end', values=periodo)

    def ver_prestamos(self):
        """Abrir ventana para ver los préstamos"""
        try:
            # Obtener información del usuario actual (asumimos que es 'admin' por ahora)
            connection = self.db_manager.connect()
            cursor = connection.cursor(dictionary=True)
            
            # Consultar información del usuario
            query = """
            SELECT id_usuario, usuario, rol
            FROM usuarios 
            WHERE usuario = 'admin'
            """
            cursor.execute(query)
            usuario_actual = cursor.fetchone()
            
            # Si el usuario es un empleado regular, obtener su id_empleado
            if usuario_actual['rol'] == 'empleado':
                query_empleado = """
                SELECT id_empleado 
                FROM empleados 
                WHERE cedula_identidad = %s
                """
                cursor.execute(query_empleado, (usuario_actual['usuario'],))
                empleado = cursor.fetchone()
                if empleado:
                    usuario_actual['id_empleado'] = empleado['id_empleado']
            
            from formularios.prestamos_form import PrestamosForm
            PrestamosForm(self, self.db_manager, usuario_actual)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir el formulario de préstamos: {str(e)}")
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()