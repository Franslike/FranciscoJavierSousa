import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import calendar
from util.ayuda import Ayuda

class AsistenciasForm(ttk.Frame):
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
            'nomina.asistencias'
        )
        
        if not alcance:
            messagebox.showerror("Error", "No tienes los permisos suficientes para acceder a este módulo.")
            self.destroy()
            return
            
        self.tiene_acceso_global = alcance == 'GLOBAL'
        
        # Constantes para la lógica de asistencias
        self.HORAS_LABORALES = 8
        self.MINUTOS_GRACIA = 15
        self.HORA_ENTRADA = "08:00"
        self.HORA_SALIDA = "17:00"
        
        # Frame principal
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Titulo
        ttk.Label(self.main_frame, text="Asistencias", font=('Helvetica', 12, 'bold')).pack(anchor='w', pady=(0,5))
        
        # Frame superior para filtros
        self.filtros_frame = ttk.LabelFrame(self.main_frame, text="Filtros", padding="5")
        self.filtros_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Filtro por empleado
        ttk.Label(self.filtros_frame, text="Empleado:").pack(side=tk.LEFT, padx=5)
        self.empleado_var = tk.StringVar()
        self.empleado_combo = ttk.Combobox(self.filtros_frame, 
                                         textvariable=self.empleado_var,
                                         state="readonly",
                                         width=30)
        self.empleado_combo.pack(side=tk.LEFT, padx=5)
        
        # Filtro por fecha
        ttk.Label(self.filtros_frame, text="Desde:").pack(side=tk.LEFT, padx=5)
        self.fecha_inicio = DateEntry(self.filtros_frame, width=12, date_pattern='dd/mm/yyyy')
        self.fecha_inicio.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.filtros_frame, text="Hasta:").pack(side=tk.LEFT, padx=5)
        self.fecha_fin = DateEntry(self.filtros_frame, width=12, date_pattern='dd/mm/yyyy')
        self.fecha_fin.pack(side=tk.LEFT, padx=5)
        
        # Botón para aplicar filtros
        ttk.Button(self.filtros_frame, text="Buscar",
                  command=self.cargar_asistencias).pack(side=tk.LEFT, padx=5)
        
        # Frame para el Treeview
        self.tree_frame = ttk.Frame(self.main_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Crear Treeview con columnas adicionales
        self.columns = ("fecha", "empleado", "cedula", "entrada", "salida", 
                       "horas_trabajadas", "estado", "observacion")
        self.tree = ttk.Treeview(self.tree_frame, columns=self.columns, show='headings')
        
        # Configurar columnas
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("empleado", text="Empleado")
        self.tree.heading("cedula", text="Cédula")
        self.tree.heading("entrada", text="Hora Entrada")
        self.tree.heading("salida", text="Hora Salida")
        self.tree.heading("horas_trabajadas", text="Horas")
        self.tree.heading("estado", text="Estado")
        self.tree.heading("observacion", text="Observación")
        
        # Configurar anchos de columna
        self.tree.column("fecha", width=100)
        self.tree.column("empleado", width=200)
        self.tree.column("cedula", width=100)
        self.tree.column("entrada", width=100)
        self.tree.column("salida", width=100)
        self.tree.column("horas_trabajadas", width=70)
        self.tree.column("estado", width=100)
        self.tree.column("observacion", width=300)
        
        # Agregar scrollbars
        self.vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        
        # Grid del tree y scrollbars
        self.tree.grid(column=0, row=0, sticky='nsew')
        self.vsb.grid(column=1, row=0, sticky='ns')
        self.hsb.grid(column=0, row=1, sticky='ew')
        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(0, weight=1)
        
        # Frame para botones de acción
        self.botones_frame = ttk.Frame(self.main_frame)
        self.botones_frame.pack(fill=tk.X, pady=5)
        
        # Botones de acción
        ttk.Button(self.botones_frame, text="Justificar Inasistencia",
                  command=self.justificar_inasistencia).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.botones_frame, text="Ver Detalles",
                  command=self.ver_detalles).pack(side=tk.LEFT, padx=5)
        
        # Configurar interfaz según permisos
        if not self.tiene_acceso_global:
            self.empleado_combo.configure(state='disabled')
            # Buscar y deshabilitar específicamente el botón de justificación
            for button in self.botones_frame.winfo_children():
                if button['text'] == "Justificar Inasistencia":
                    button.configure(state='disabled')
                    
            # Obtener información del empleado
            query = """
            SELECT nombre, apellido, cedula_identidad 
            FROM empleados 
            WHERE id_empleado = %s
            """
            empleado = self.db_manager.ejecutar_query(query, (self.usuario_actual['id_empleado'],), fetchone=True)
            if empleado:
                self.empleado_var.set(f"{empleado[0]} {empleado[1]} - {empleado[2]}")
            self.empleado_combo.configure(state='disabled')
        
        # Configurar estilos visuales para estados
        self.tree.tag_configure('retardo', background='#fff3cd')     # Amarillo claro
        self.tree.tag_configure('presente', background='#d4edda')    # Verde claro
        self.tree.tag_configure('ausente', background='#f8d7da')     # Rojo claro
        self.tree.tag_configure('justificado', background='#cce5ff') # Azul claro
        self.tree.tag_configure('incompleto', background='#fff3cd')  # Amarillo claro
        
        # Cargar empleados en el combo
        self.cargar_empleados()

    def mostrar_ayuda(self, event=None):
        """Muestra la ayuda contextual del módulo de empleados"""
        self.sistema_ayuda.mostrar_ayuda('asistencias')
        
    def cargar_empleados(self):
        """
        Carga la lista de empleados en el combobox de filtro
        """
        try:
            # Obtener la lista de empleados de la base de datos
            empleados = self.db_manager.ver_empleados()

            # Filtrar solo empleados activos
            empleados_activos = [emp for emp in empleados if len(emp) <= 7 or emp[7].lower() != 'inactivo']
            
            # Formatear los valores para el combobox
            valores_combo = [""]  # Opción vacía para mostrar todos
            valores_combo.extend([
                f"{emp[1]} {emp[2]} - {emp[3]}"  # nombre apellido - cédula
                for emp in empleados_activos
            ])
            
            # Actualizar el combobox
            self.empleado_combo['values'] = valores_combo
            
        except Exception as e:
            print(f"Error al cargar empleados: {e}")
            messagebox.showerror(
                "Error",
                "No se pudieron cargar los empleados. Por favor, verifique la conexión a la base de datos."
            )

        # Agregar un binding para la selección
        self.empleado_combo.bind('<<ComboboxSelected>>', self.on_empleado_selected)

    def on_empleado_selected(self, event=None):
        """
        Manejador del evento de selección de empleado
        """
        if self.empleado_var.get():
            # Si se seleccionó un empleado, actualizar la lista de asistencias
            self.cargar_asistencias()
        else:
            # Si se seleccionó la opción vacía, mostrar todos los empleados
            self.cargar_asistencias()

    def cargar_asistencias(self):
        # Limpiar Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        fecha_inicio = self.fecha_inicio.get_date()
        fecha_fin = self.fecha_fin.get_date()
        
        # Obtener empleado seleccionado
        id_empleado = None
        if self.empleado_var.get():
            if not self.tiene_acceso_global:
                id_empleado = self.usuario_actual['id_empleado']
            else:
                cedula = self.empleado_var.get().split('-')[1].strip()
                empleados = self.db_manager.ver_empleados()
                empleados_activos = [emp for emp in empleados if len(emp) <= 7 or emp[7].lower() != 'inactivo']
                for emp in empleados_activos:
                    if emp[3] == cedula:
                        id_empleado = emp[0]
                        break
        try:
            # Obtener registros
            registros = self.db_manager.obtener_asistencias(fecha_inicio, fecha_fin, id_empleado)

            empleados_activos = [emp for emp in self.db_manager.ver_empleados() if len(emp) <= 7 or emp[7].lower() != 'inactivo']
            cedulas_activas = {emp[3] for emp in empleados_activos}
        
            for registro in registros:
                # Verificar si el empleado está activo
                cedula_empleado = registro[2]
                if cedula_empleado not in cedulas_activas:
                    continue

                fecha = registro[0]
                empleado = registro[1]
                cedula = registro[2]
            
                # Manejar diferentes tipos de datos para entrada y salida
                entrada = None
                if registro[3]:
                    if isinstance(registro[3], datetime):
                        entrada = registro[3].strftime('%H:%M')
                    elif isinstance(registro[3], str):
                        # Si ya es string, verificar si tiene formato de hora
                        try:
                            entrada = datetime.strptime(registro[3], '%H:%M:%S').strftime('%H:%M')
                        except ValueError:
                            try:
                                entrada = datetime.strptime(registro[3], '%H:%M').strftime('%H:%M')
                            except ValueError:
                                entrada = registro[3]
                    elif isinstance(registro[3], timedelta):
                        # Si es timedelta, convertir a formato de hora
                        segundos = registro[3].total_seconds()
                        horas = int(segundos // 3600)
                        minutos = int((segundos % 3600) // 60)
                        entrada = f"{horas:02d}:{minutos:02d}"
                
                salida = None
                if registro[4]:
                    if isinstance(registro[4], datetime):
                        salida = registro[4].strftime('%H:%M')
                    elif isinstance(registro[4], str):
                        try:
                            salida = datetime.strptime(registro[4], '%H:%M:%S').strftime('%H:%M')
                        except ValueError:
                            try:
                                salida = datetime.strptime(registro[4], '%H:%M').strftime('%H:%M')
                            except ValueError:
                                salida = registro[4]
                    elif isinstance(registro[4], timedelta):
                        segundos = registro[4].total_seconds()
                        horas = int(segundos // 3600)
                        minutos = int((segundos % 3600) // 60)
                        salida = f"{horas:02d}:{minutos:02d}"
                
                estado_actual = registro[5]
                observacion = registro[6]
                
                # Calcular estado y horas trabajadas
                estado, horas, obs = self.calcular_estado_asistencia(entrada, salida, estado_actual)
                
                # Si hay una observación previa, mantenerla
                if observacion:
                    obs = observacion
                
                valores = [
                    fecha if isinstance(fecha, str) else fecha.strftime('%d-%m-%Y'),
                    empleado,
                    cedula,
                    entrada or '',
                    salida or '',
                    f"{horas:.1f}" if horas > 0 else '',
                    estado,
                    obs
                ]
                
                # Asignar tag según estado
                self.tree.insert('', 'end', values=valores, tags=(estado.lower(),))

        except Exception as e:
            print(f"Error al cargar asistencias: {e}")
            messagebox.showerror(
                "Error",
                "No se pudieron cargar las asistencias. Por favor, verifique la conexión a la base de datos.")

    def formatear_hora(self, tiempo):
        """
        Formatea un objeto de tiempo en string HH:MM
        """
        if isinstance(tiempo, datetime):
            return tiempo.strftime('%H:%M')
        elif isinstance(tiempo, str):
            try:
                return datetime.strptime(tiempo, '%H:%M:%S').strftime('%H:%M')
            except ValueError:
                try:
                    return datetime.strptime(tiempo, '%H:%M').strftime('%H:%M')
                except ValueError:
                    return tiempo
        elif isinstance(tiempo, timedelta):
            segundos = tiempo.total_seconds()
            horas = int(segundos // 3600)
            minutos = int((segundos % 3600) // 60)
            return f"{horas:02d}:{minutos:02d}"
        return None

    def calcular_estado_asistencia(self, entrada, salida, estado_actual=None):
        """
        Calcula el estado de la asistencia basado en las horas trabajadas y los horarios.
        Si trabaja menos de 4 horas se considera inasistencia.
        """
        if estado_actual == 'Justificada':
            return 'Justificada', 8.0, "Asistencia justificada"
            
        if not entrada:
            return 'Ausente', 0.0, "No se registró entrada"
            
        # Convertir strings a datetime
        try:
            if isinstance(entrada, str):
                hora_entrada = datetime.strptime(entrada, '%H:%M').time()
            else:
                return 'Error', 0.0, "Formato de entrada inválido"
                
            if salida:
                if isinstance(salida, str):
                    hora_salida = datetime.strptime(salida, '%H:%M').time()
                else:
                    return 'Error', 0.0, "Formato de salida inválido"
            else:
                hora_salida = None
                
            hora_inicio_esperada = datetime.strptime(self.HORA_ENTRADA, '%H:%M').time()
        except ValueError:
            return 'Error', 0.0, "Error en formato de hora"
            
        # Si no hay salida
        if not hora_salida:
            return 'Incompleto', 0.0, "Falta registro de salida"
            
        # Calcular horas trabajadas
        entrada_dt = datetime.combine(datetime.today(), hora_entrada)
        salida_dt = datetime.combine(datetime.today(), hora_salida)
        
        if salida_dt < entrada_dt:
            salida_dt += timedelta(days=1)
            
        horas_trabajadas = (salida_dt - entrada_dt).total_seconds() / 3600
        
        # Si trabajó menos de 4 horas, se considera inasistencia
        if horas_trabajadas < 4:
            return 'Ausente', 0.0, f"Trabajó menos de media jornada ({horas_trabajadas:.1f} hrs)"
            
        # Verificar retardo
        minutos_retardo = (entrada_dt - datetime.combine(datetime.today(), hora_inicio_esperada)).total_seconds() / 60
        
        if minutos_retardo > self.MINUTOS_GRACIA:
            return 'Retardo', horas_trabajadas, f"Retardo de {int(minutos_retardo)} minutos"
            
        # Verificar horas mínimas
        if horas_trabajadas < self.HORAS_LABORALES:
            return 'Incompleto', horas_trabajadas, f"Jornada incompleta ({horas_trabajadas:.1f} hrs)"
            
        return 'Presente', horas_trabajadas, "Asistencia completa"


    def justificar_inasistencia(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un registro")
            return
            
        item = self.tree.item(selected[0])
        fecha = item['values'][0]
        empleado = item['values'][1]
        cedula = item['values'][2]
        estado = item['values'][6]

        if estado == 'Justificada':
            messagebox.showinfo("Información", "Esta asistencia ya está justificada")
            return
        
        if estado == 'Presente':
            messagebox.showinfo("Información", "No se pueden justificar asistencias completas")
            return
            
        dialog = tk.Toplevel(self)
        dialog.title("Justificar Inasistencia/Registro Incompleto")
        dialog.geometry("500x680")
        
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Información del empleado
        info_frame = ttk.LabelFrame(main_frame, text="Información", padding="10")
        info_frame.pack(fill=tk.X, pady=(0,15))
        
        campos = [
            ("Empleado:", empleado),
            ("Cédula:", cedula),
            ("Fecha:", fecha),
            ("Estado actual:", estado)
        ]
        
        for i, (label, value) in enumerate(campos):
            ttk.Label(info_frame, text=label, font=('Helvetica', 9, 'bold')).grid(
                row=i, column=0, sticky='e', padx=5, pady=2)
            ttk.Label(info_frame, text=value).grid(
                row=i, column=1, sticky='w', padx=5, pady=2)

        # Tipo de justificativo
        ttk.Label(main_frame, text="Tipo de Justificativo:").pack(fill=tk.X, pady=5)
        tipo_var = tk.StringVar(value="Médico")
        tipo_combo = ttk.Combobox(main_frame, textvariable=tipo_var,
                            values=["Médico", "Permiso", "Otros"],
                            state="readonly")
        tipo_combo.pack(fill=tk.X, pady=5)

        # Frames para motivo y observación
        motivo_frame = ttk.Frame(main_frame)
        observacion_frame = ttk.Frame(main_frame)
        
        ttk.Label(motivo_frame, text="Motivo:").pack(fill=tk.X)
        motivo_text = tk.Text(motivo_frame, height=4)
        motivo_text.pack(fill=tk.X, pady=5)

        ttk.Label(observacion_frame, text="Observación:").pack(fill=tk.X)
        observacion_text = tk.Text(observacion_frame, height=4)
        observacion_text.pack(fill=tk.X, pady=5)

        # Frame para documento
        doc_frame = ttk.LabelFrame(main_frame, text="Documento de Respaldo", padding="10")
        doc_frame.pack(fill=tk.X, pady=15)

        archivo_var = tk.StringVar()
        ttk.Label(doc_frame, textvariable=archivo_var).pack(fill=tk.X, pady=5)

        def seleccionar_archivo():
            filetypes = [
                ('Documentos PDF', '*.pdf'),
                ('Imágenes', '*.png *.jpg *.jpeg')
            ]
            archivo = filedialog.askopenfilename(filetypes=filetypes)
            if archivo:
                archivo_var.set(archivo)
                return archivo
            return None

        seleccionar_btn = tk.Button(
            doc_frame,
            text="Seleccionar Archivo",
            font=("Arial", 10),
            fg="#ffffff",
            bg="#475569",
            activebackground="#334155",
            relief="flat",
            cursor="hand2",
            pady=5,
            command=seleccionar_archivo
        )
        seleccionar_btn.pack(pady=5)

        def on_tipo_change(*args):
            tipo = tipo_var.get()
            if tipo in ["Médico", "Permiso"]:
                motivo_frame.pack_forget()
                
                observacion_frame.pack(fill=tk.X, pady=5)
                observacion_text.configure(state='normal')
                observacion_text.delete('1.0', tk.END)
                observacion_text.insert('1.0', f"Justificado por documento {tipo.lower()}")
                observacion_text.configure(state='disabled')
                
                for widget in doc_frame.winfo_children():
                    if isinstance(widget, ttk.Label) and widget.cget("text") == "*Requerido":
                        widget.destroy()
                ttk.Label(doc_frame, text="*Requerido", foreground="red").pack(before=seleccionar_btn)
            else:
                motivo_frame.pack(fill=tk.X, pady=5, before=doc_frame)
                observacion_frame.pack(fill=tk.X, pady=5, before=doc_frame)
                observacion_text.configure(state='normal')
                observacion_text.delete('1.0', tk.END)
                
                for widget in doc_frame.winfo_children():
                    if isinstance(widget, ttk.Label) and widget.cget("text") == "*Requerido":
                        widget.destroy()

        tipo_var.trace('w', on_tipo_change)
        on_tipo_change()

        def guardar_justificacion():
            tipo = tipo_var.get()
            if tipo in ["Médico", "Permiso"]:
                if not archivo_var.get():
                    messagebox.showwarning("Advertencia", "El documento es requerido para justificativos médicos/permisos")
                    return
            else:
                if not motivo_text.get("1.0", tk.END).strip():
                    messagebox.showwarning("Advertencia", "El motivo es requerido")
                    return

            try:
                fecha_mysql = datetime.strptime(fecha, '%d-%m-%Y').strftime('%Y-%m-%d')
                archivo_ruta = archivo_var.get()
                
                if archivo_ruta:
                    directorio = "justificantes"
                    if not os.path.exists(directorio):
                        os.makedirs(directorio)
                    
                    extension = os.path.splitext(archivo_ruta)[1]
                    nuevo_nombre = f"{cedula}_{fecha.replace('/','-')}_{tipo_var.get()}{extension}"
                    destino = os.path.join(directorio, nuevo_nombre)
                    shutil.copy2(archivo_ruta, destino)
                
                datos_justificativo = {
                    'empleado_id': self.db_manager.obtener_empleado_por_cedula(cedula)[0],
                    'fecha': fecha_mysql,
                    'tipo': tipo_var.get(),
                    'motivo': motivo_text.get("1.0", tk.END).strip() if tipo not in ["Médico", "Permiso"] else "",
                    'observacion': observacion_text.get("1.0", tk.END).strip(),
                    'num_documento': nuevo_nombre if archivo_ruta else None,
                    'registrado_por': f"{self.usuario_actual['nombre']} {self.usuario_actual['apellido']}"
                }

                self.db_manager.registrar_justificacion(datos_justificativo)
                
                detalle = (f"Justificación de inasistencia:\n"
                        f"Empleado: {empleado}\n"
                        f"Fecha: {fecha}\n"
                        f"Tipo: {tipo_var.get()}\n"
                        f"Motivo: {datos_justificativo['motivo']}\n"
                        f"Documento adjunto: {nuevo_nombre if archivo_ruta else 'No adjuntado'}\n"
                        f"Registrado por: {self.usuario_actual['nombre']} {self.usuario_actual['apellido']}")

                self.db_manager.registrar_auditoria(
                    usuario=f"{self.usuario_actual['nombre']} {self.usuario_actual['apellido']}",
                    accion='Justificó inasistencia',
                    tabla='justificativos',
                    detalle=detalle)
                messagebox.showinfo("Éxito", "Justificación registrada correctamente")
                dialog.destroy()
                self.cargar_asistencias()

            except Exception as e:
                messagebox.showerror("Error", f"Error al registrar justificación: {str(e)}")

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        guardar_btn = tk.Button(
        button_frame,
        text="Guardar Justificación",
        font=("Arial", 10, "bold"),
        fg="#ffffff",
        bg="#2596be",
        activebackground="#1e7aa3",
        activeforeground="#ffffff", 
        relief="flat",
        cursor="hand2",
        width=20,
        pady=8,
        command=guardar_justificacion
        )
        guardar_btn.pack(side=tk.LEFT, padx=5)

        cancelar_btn = tk.Button(
        button_frame,
        text="Cancelar",
        font=("Arial", 10, "bold"),
        fg="#ffffff",
        bg="#6C757D",
        activebackground="#5C636A",
        relief="flat",
        cursor="hand2",
        width=20,
        pady=8,
        command=dialog.destroy
        )
        cancelar_btn.pack(side=tk.LEFT, padx=5)

        # Centrar ventana
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')

    def ver_detalles(self):
        """Muestra una ventana con los detalles completos del registro de asistencia seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione una asistencia")
            return
            
        item = self.tree.item(selected[0])
        valores = item['values']
        
        detalles_window = tk.Toplevel(self)
        detalles_window.title("Detalles de Asistencia")
        detalles_window.geometry("420x620")
        detalles_window.configure(bg='white')
        
        # Crear estilos
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Info.TLabel', font=('Arial', 10))
        
        # Frame principal
        frame = ttk.Frame(detalles_window, padding="20", style='Card.TFrame')
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título y separador
        ttk.Label(frame, text="Información", style='Subtitle.TLabel').grid(
            row=0, column=0, columnspan=2, sticky='w', pady=(0,10))
        ttk.Separator(frame, orient='horizontal').grid(
            row=1, column=0, columnspan=2, sticky='ew', pady=(0,10))

        # Información principal
        info = {
            "Empleado": valores[1],
            "Cédula": valores[2],
            "Fecha": valores[0],
            "Estado actual": valores[6]
        }

        row = 2
        for label, value in info.items():
            ttk.Label(frame, text=f"{label}:", font=('Arial', 10, 'bold')).grid(
                row=row, column=0, sticky='e', pady=5)
            ttk.Label(frame, text=str(value), wraplength=300).grid(
                row=row, column=1, sticky='w', pady=5, padx=10)
            row += 1

        # Separador después de información principal
        ttk.Separator(frame, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky='ew', pady=10)
        row += 1

        # Sección de Detalles del Registro
        ttk.Label(frame, text="Detalles del Registro", style='Subtitle.TLabel').grid(
            row=row, column=0, columnspan=2, sticky='w', pady=(0,10))
        row += 1

        detalles = {
            "Hora de Entrada": valores[3] or "No registrada",
            "Hora de Salida": valores[4] or "No registrada",
            "Horas Trabajadas": valores[5] or "0.0",
            "Observación": valores[7]
        }

        for label, value in detalles.items():
            ttk.Label(frame, text=f"{label}:", font=('Arial', 10, 'bold')).grid(
                row=row, column=0, sticky='e', pady=5)
            ttk.Label(frame, text=str(value), wraplength=300).grid(
                row=row, column=1, sticky='w', pady=5, padx=10)
            row += 1

        # Separador después de detalles
        ttk.Separator(frame, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky='ew', pady=10)
        row += 1
            
        # Si hay justificación, mostrar detalles adicionales
        if valores[6] == 'Justificada':
            try:
                fecha_obj = datetime.strptime(valores[0], '%d-%m-%Y')
                fecha_mysql = fecha_obj.strftime('%Y-%m-%d')
                
                justificacion = self.db_manager.obtener_justificacion(valores[2], fecha_mysql)
                
                if justificacion:
                    ttk.Label(frame, text="Detalles de Justificación", 
                            style='Subtitle.TLabel').grid(
                        row=row, column=0, columnspan=2, sticky='w', pady=(0,10))
                    row += 1
                    
                    detalles_just = {
                        "Tipo": justificacion[0],
                        "Motivo": justificacion[1],
                        "Documento": justificacion[2] or "No especificado",
                        "Registrado por": justificacion[3],
                        "Fecha de registro": justificacion[4].strftime('%d-%m-%Y %H:%M:%S')
                    }
                    
                    for label, value in detalles_just.items():
                        ttk.Label(frame, text=f"{label}:", 
                                font=('Arial', 10, 'bold')).grid(
                            row=row, column=0, sticky='e', pady=5)
                        ttk.Label(frame, text=str(value),
                                wraplength=300).grid(
                            row=row, column=1, sticky='w', pady=5, padx=10)
                        row += 1
                        
            except Exception as e:
                print(f"Error al obtener detalles de justificación: {e}")

        # Botón Cerrar
        close_btn = tk.Button(
            frame,
            text="Cerrar",
            font=('Arial', 10, "bold"),
            fg='white',
            bg='#6C757D',
            activebackground='#5C636A',
            relief='flat',
            cursor='hand2',
            command=detalles_window.destroy
        )
        close_btn.grid(row=row, column=0, columnspan=2, pady=20)

        # Configurar padding consistente
        for widget in frame.winfo_children():
            widget.grid_configure(padx=15)

        # Centrar ventana
        detalles_window.update_idletasks()
        width = detalles_window.winfo_width()
        height = detalles_window.winfo_height()
        x = (detalles_window.winfo_screenwidth() // 2) - (width // 2)
        y = (detalles_window.winfo_screenheight() // 2) - (height // 2)
        detalles_window.geometry(f'{width}x{height}+{x}+{y}')