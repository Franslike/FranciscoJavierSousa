import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import calendar

class AsistenciasForm(ttk.Frame):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        
        self.pack(fill=tk.BOTH, expand=True)
        
        # Constantes para la lógica de asistencias
        self.HORAS_LABORALES = 8
        self.MINUTOS_GRACIA = 15
        self.HORA_ENTRADA = "08:00"
        self.HORA_SALIDA = "17:00"
        
        # Frame principal
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
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
        self.fecha_inicio = DateEntry(self.filtros_frame, width=12)
        self.fecha_inicio.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.filtros_frame, text="Hasta:").pack(side=tk.LEFT, padx=5)
        self.fecha_fin = DateEntry(self.filtros_frame, width=12)
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
        
        # Configurar estilos visuales para estados
        self.tree.tag_configure('retardo', background='#fff3cd')     # Amarillo claro
        self.tree.tag_configure('presente', background='#d4edda')    # Verde claro
        self.tree.tag_configure('ausente', background='#f8d7da')     # Rojo claro
        self.tree.tag_configure('justificado', background='#cce5ff') # Azul claro
        self.tree.tag_configure('incompleto', background='#fff3cd')  # Amarillo claro
        
        # Cargar empleados en el combo
        self.cargar_empleados()
        
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
        """
        Carga las asistencias con la nueva lógica de estados y horas trabajadas
        """
        # Limpiar Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        fecha_inicio = self.fecha_inicio.get_date()
        fecha_fin = self.fecha_fin.get_date()
        
        # Obtener empleado seleccionado
        id_empleado = None
        if self.empleado_var.get():
            cedula = self.empleado_var.get().split('-')[1].strip()
            empleados = self.db_manager.ver_empleados()

            # Filtrar solo empleados activos
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
                    fecha.strftime('%Y-%m-%d') if isinstance(fecha, datetime) else fecha,
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
        
        # Verificar retardo
        minutos_retardo = (entrada_dt - datetime.combine(datetime.today(), hora_inicio_esperada)).total_seconds() / 60
        
        if minutos_retardo > self.MINUTOS_GRACIA:
            return 'Retardo', horas_trabajadas, f"Retardo de {int(minutos_retardo)} minutos"
            
        # Verificar horas mínimas
        if horas_trabajadas < self.HORAS_LABORALES:
            return 'Incompleto', horas_trabajadas, f"Jornada incompleta ({horas_trabajadas:.1f} hrs)"
            
        return 'Presente', horas_trabajadas, "Asistencia completa"

    def justificar_inasistencia(self):
        """
        Justifica una inasistencia y establece las horas trabajadas en 8
        """
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un registro")
            return
            
        # Obtener datos del registro seleccionado
        item = self.tree.item(selected[0])
        estado = item['values'][6]  # Índice del estado
        
        if estado == 'Justificada':
            messagebox.showinfo("Información", "Esta asistencia ya está justificada")
            return
        
        if estado == 'Presente':
            messagebox.showinfo("Información", "No se pueden justificar asistencias completas")
            return
            
        # Crear ventana de justificación con la lógica existente...
        # [El resto del código de justificación permanece igual]

    def justificar_inasistencia(self):
        """
        Justificar una inasistencia o registro incompleto
        """
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un registro")
            return
            
        # Obtener datos del registro seleccionado
        item = self.tree.item(selected[0])
        fecha = item['values'][0]  # Fecha
        empleado = item['values'][1]  # Nombre del empleado
        cedula = item['values'][2]  # Cédula
        estado = item['values'][6]  # Estado

        # Validar el estado
        if estado == 'Justificada':
            messagebox.showinfo("Información", "Esta asistencia ya está justificada")
            return
        
        if estado == 'Presente':
            messagebox.showinfo("Información", "No se pueden justificar asistencias completas")
            return
            
        # Crear ventana de justificación
        self.justificar_window = tk.Toplevel(self)
        self.justificar_window.title("Justificar Inasistencia/Registro Incompleto")
        self.justificar_window.geometry("500x600")
        
        # Frame principal
        frame = ttk.Frame(self.justificar_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Mostrar información del empleado
        ttk.Label(frame, text=f"Empleado: {empleado}").pack(fill=tk.X, pady=5)
        ttk.Label(frame, text=f"Cédula: {cedula}").pack(fill=tk.X, pady=5)
        ttk.Label(frame, text=f"Fecha: {fecha}").pack(fill=tk.X, pady=5)
        ttk.Label(frame, text=f"Estado actual: {estado}").pack(fill=tk.X, pady=5)
        
        # Tipo de justificativo
        ttk.Label(frame, text="Tipo de Justificativo:").pack(fill=tk.X, pady=5)
        tipo_var = tk.StringVar(value="Médico")
        tipos_justificativo = ["Médico", "Permiso", "Otros"]
        tipo_combo = ttk.Combobox(frame, textvariable=tipo_var, 
                                values=tipos_justificativo, state="readonly")
        tipo_combo.pack(fill=tk.X, pady=5)
        
        # Motivo
        ttk.Label(frame, text="Motivo:").pack(fill=tk.X, pady=5)
        motivo_text = tk.Text(frame, height=4)
        motivo_text.pack(fill=tk.X, pady=5)
        
        # Observación
        ttk.Label(frame, text="Observación:").pack(fill=tk.X, pady=5)
        observacion_text = tk.Text(frame, height=4)
        observacion_text.pack(fill=tk.X, pady=5)
        
        # Documento respaldo
        ttk.Label(frame, text="N° de Documento de Respaldo:").pack(fill=tk.X, pady=5)
        doc_entry = ttk.Entry(frame)
        doc_entry.pack(fill=tk.X, pady=5)

        def guardar_justificacion():
            # Validar campos requeridos
            motivo = motivo_text.get("1.0", tk.END).strip()
            if not motivo:
                messagebox.showwarning("Advertencia", "Por favor ingrese el motivo")
                return

            try:
                # Obtener el ID del empleado
                connection = self.db_manager.connect()
                cursor = connection.cursor()
                cursor.execute("SELECT id_empleado FROM empleados WHERE cedula_identidad = %s", (cedula,))
                result = cursor.fetchone()
                
                if not result:
                    messagebox.showerror("Error", "No se encontró el empleado en la base de datos")
                    return
                    
                empleado_id = result[0]

                # Preparar datos de la justificación
                datos_justificativo = {
                    'empleado_id': empleado_id,
                    'fecha': fecha,
                    'tipo': tipo_var.get(),
                    'motivo': motivo,
                    'observacion': observacion_text.get("1.0", tk.END).strip(),
                    'num_documento': doc_entry.get().strip(),
                    'registrado_por': 'admin'  # Aquí deberías usar el usuario actual del sistema
                }

                # Registrar la justificación
                self.db_manager.registrar_justificacion(datos_justificativo)
                messagebox.showinfo("Éxito", "Justificación registrada correctamente")
                self.justificar_window.destroy()
                self.cargar_asistencias()  # Recargar la lista de asistencias

            except Exception as e:
                messagebox.showerror("Error", f"Error al registrar justificación: {str(e)}")
                print(f"Error detallado: {str(e)}")  # Para debugging
            finally:
                if 'connection' in locals() and connection.is_connected():
                    cursor.close()
                    connection.close()

        # Botones
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Guardar",
                command=guardar_justificacion).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar",
                command=self.justificar_window.destroy).pack(side=tk.LEFT, padx=5)

    def ver_detalles(self):
        """Muestra una ventana con los detalles completos del registro de asistencia seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione una asistencia")
            return
            
        # Obtener datos del registro seleccionado
        item = self.tree.item(selected[0])
        valores = item['values']
        
        # Crear ventana de detalles
        detalles_window = tk.Toplevel(self)
        detalles_window.title("Detalles de Asistencia")
        detalles_window.geometry("500x400")
        
        # Frame principal
        frame = ttk.Frame(detalles_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Información detallada
        info = {
            "Fecha": valores[0],
            "Empleado": valores[1],
            "Cédula": valores[2],
            "Hora de Entrada": valores[3] or "No registrada",
            "Hora de Salida": valores[4] or "No registrada",
            "Horas Trabajadas": valores[5] or "0.0",
            "Estado": valores[6],
            "Observación": valores[7]
        }
        
        # Mostrar información
        row = 0
        for label, value in info.items():
            ttk.Label(frame, text=f"{label}:", font=('Arial', 10, 'bold')).grid(
                row=row, column=0, sticky='w', pady=5)
            ttk.Label(frame, text=str(value), wraplength=300).grid(
                row=row, column=1, sticky='w', pady=5, padx=10)
            row += 1
            
        # Si hay justificación, mostrar detalles adicionales
        if valores[6] == 'Justificada':
            # Obtener detalles de la justificación desde la base de datos
            try:
                justificacion = self.db_manager.obtener_justificacion(
                    valores[2],  # cédula
                    valores[0]   # fecha
                )
                if justificacion:
                    ttk.Label(frame, text="\nDetalles de Justificación:", 
                             font=('Arial', 11, 'bold')).grid(
                        row=row, column=0, columnspan=2, sticky='w', pady=10)
                    row += 1
                    
                    detalles_just = {
                        "Tipo": justificacion[0],
                        "Motivo": justificacion[1],
                        "Documento": justificacion[2] or "No especificado",
                        "Registrado por": justificacion[3],
                        "Fecha de registro": justificacion[4].strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    for label, value in detalles_just.items():
                        ttk.Label(frame, text=f"{label}:", 
                                font=('Arial', 10, 'bold')).grid(
                            row=row, column=0, sticky='w', pady=5)
                        ttk.Label(frame, text=str(value), 
                                wraplength=300).grid(
                            row=row, column=1, sticky='w', pady=5, padx=10)
                        row += 1
                        
            except Exception as e:
                print(f"Error al obtener detalles de justificación: {e}")
        
        # Botón para cerrar
        ttk.Button(frame, text="Cerrar", 
                  command=detalles_window.destroy).grid(
            row=row, column=0, columnspan=2, pady=20)