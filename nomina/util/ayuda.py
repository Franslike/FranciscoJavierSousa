import tkinter as tk
from tkinter import ttk
import webbrowser
from PIL import Image, ImageTk
import os

class Ayuda:
    def __init__(self):
        # Definimos todo el contenido de ayuda organizado por módulos
        self.contenido_ayuda = {
            'empleados': {
                'titulo': 'Módulo de Empleados',
                'contenido': """
                El módulo de empleados permite gestionar la información del personal:
                
                • Registro de nuevos empleados
                • Actualización de datos personales
                • Gestión de documentos
                
                Operaciones principales:
                1. Para registrar un empleado nuevo, use el botón 'Nuevo Empleado'
                [img]boton_nuevo_empleado.png[/img]
                [img]registro_empleado.png[/img]
                2. Para editar información, seleccione un empleado y use 'Ver Detalles'
                [img]seleccionar_empleado.png[/img]
                [img]detalles_empleado.png[/img]
                3. Para cambiar el estado, use el botón 'Cambiar Status'
                [img]boton_cambiar_status.png[/img]
                [img]cambiar_status.png[/img]
                """,
                'imagenes': {	
                    'boton_nuevo_empleado.png': './imagenes/ayuda/boton_nuevo_empleado.png',
                    'registro_empleado.png': './imagenes/ayuda/registro_empleado.png',
                    'seleccionar_empleado.png': './imagenes/ayuda/seleccionar_empleado.png',
                    'detalles_empleado.png': './imagenes/ayuda/detalles_empleado.png',
                    'boton_cambiar_status.png': './imagenes/ayuda/boton_cambiar_status.png',
                    'cambiar_status.png': './imagenes/ayuda/cambiar_status.png'
                },
                 'atajos': {
                     'F1': 'Mostrar esta ayuda',
                     'F5': 'Actualizar lista',
                     'Doble clic': 'Ver detalles del empleado'
                 }
            },
            'nfc': {
                'titulo': 'Módulo de Administración NFC',
                'contenido': """
                El módulo NFC permite gestionar las tarjetas de acceso del personal:
                
                • Registro de nuevas tarjetas NFC
                • Asignación de tarjetas a empleados
                • Control de estado de dispositivos
                
                Operaciones principales:
                1. Para registrar una tarjeta, ingrese el UID en el campo superior y use 'Registrar Tarjeta'
                [img]boton_registrar_nfc.png[/img]
                2. Las tarjetas pueden estar en estado: Disponible, Asignado o Suspendido
                [img]estado_nfc.png[/img]
                3. Use 'Marcar como Disponible' para liberar una tarjeta asignada
                [img]boton_disponible_nfc.png[/img]
                4. Las tarjetas en estado disponible pueden ser eliminadas del sistema
                [img]eliminar_nfc.png[/img]
                """,
                'imagenes': {
                    'boton_registrar_nfc.png': './imagenes/ayuda/boton_registrar_nfc.png',
                    'estado_nfc.png': './imagenes/ayuda/estado_nfc.png',
                    'boton_disponible_nfc.png': './imagenes/ayuda/boton_disponible_nfc.png',
                    'eliminar_nfc.png': './imagenes/ayuda/eliminar_nfc.png'
                }
            },
            'usuarios': {

                'titulo': 'Módulo de Usuarios',
                'contenido': """
                El módulo de usuarios permite gestionar los accesos al sistema:
                
                • Gestión de cuentas de usuario
                • Asignación de permisos
                • Bloqueo/desbloqueo de cuentas
                • Reseteo de contraseñas
                
                Operaciones principales:
                1. Para desbloquear una cuenta bloqueada, use 'Desbloquear Usuario'
                [img]desbloquear_usuario.png[/img]
                2. Para reestablecer contraseña de un usuario, use 'Reestablecer Contraseña'
                [img]reestablecer_usuario.png[/img]
                3. Use 'Cambiar Status' para activar o desactivar un usuario
                [img]cambiar_estado_usuario.png[/img]
                4. Para modificar permisos, use 'Gestionar Permisos'
                [img]boton_permisos_usuario.png[/img]
                [img]gestion_permisos.png[/img]
                """,
                'imagenes': {
                    'desbloquear_usuario.png': './imagenes/ayuda/desbloquear_usuario.png',
                    'reestablecer_usuario.png': './imagenes/ayuda/reestablecer_usuario.png',
                    'cambiar_estado_usuario.png': './imagenes/ayuda/cambiar_estado_usuario.png',
                    'boton_permisos_usuario.png': './imagenes/ayuda/boton_permisos_usuario.png',
                    'gestion_permisos.png': './imagenes/ayuda/gestion_permisos.png'
                }
            },
            'prenomina': {
                'titulo': 'Módulo de Prenómina',
                'contenido': """
                El módulo de prenómina permite calcular y gestionar los pagos del personal:

                • Cálculo automático de salarios
                • Gestión de deducciones
                • Procesamiento por períodos
                • Generación de recibos de pago

                Operaciones principales:

                1. Seleccione un período de nómina activo
                [img]seleccionar_periodo_prenomina.png[/img]
                2. Verifique los cálculos generados automáticamente
                [img]calculos_prenomina.png[/img]
                3. Procese la nómina usando 'Procesar Nómina'
                [img]boton_procesar_nomina.png[/img]
                4. Los recibos se generarán en formato PDF
                [img]recibo_nomina.png[/img]
                """,
                'imagenes': {
                    'seleccionar_periodo_prenomina.png': './imagenes/ayuda/seleccionar_periodo_prenomina.png',
                    'calculos_prenomina.png': './imagenes/ayuda/calculos_prenomina.png',
                    'boton_procesar_nomina.png': './imagenes/ayuda/boton_procesar_nomina.png',
                    'recibo_nomina.png': './imagenes/ayuda/recibo_nomina.png'
                }
            },
            'asistencias': {
                'titulo': 'Módulo de Asistencias',
                'contenido': """
                El módulo de asistencias permite gestionar el control de entrada y salida:
                
                • Visualización de registros de asistencia
                • Justificación de inasistencias
                • Control de retardos
                
                Operaciones principales:
                1. Use los filtros de fecha para ver asistencias específicas
                [img]fecha_asistencias.png[/img]
                2. Seleccione un registro y use 'Justificar Inasistencia' cuando sea necesario
                [img]boton_justificar_inasistencia.png[/img]
                [img]justificar_inasistencia.png[/img]
                3. Use 'Ver Detalles' para más información sobre un registro
                [img]boton_ver_detalles.png[/img]
                [img]detalles_asistencia.png[/img]
                """,
                'imagenes': {
                    'fecha_asistencias.png': './imagenes/ayuda/fecha_asistencias.png',
                    'boton_justificar_inasistencia.png': './imagenes/ayuda/boton_justificar_inasistencia.png',
                    'justificar_inasistencia.png': './imagenes/ayuda/justificar_inasistencia.png',
                    'boton_ver_detalles.png': './imagenes/ayuda/boton_ver_detalles.png',
                    'detalles_asistencia.png': './imagenes/ayuda/detalles_asistencia.png'
                }
            },
            'periodos': {
                'titulo': 'Módulo de Períodos de Pago',
                'contenido': """
                El módulo de períodos de pago permite gestionar los ciclos de nómina:
                
                • Creación de nuevos períodos
                • Cierre de periodos
                • Historial de cambios
                • Control de fechas y estados
                
                Operaciones principales:
                1. Para crear un nuevo período, configure las fechas de inicio y fin del período
                [img]fecha_periodo.png[/img]
                2. Luego de configurar las fechas use el botón 'Crear Período'
                [img]boton_crear_periodo.png[/img]
                3. Para ver la fecha de cierre de un periodo use el botón 'Ver Historial'
                [img]historial_periodo.png[/img] 
                4. Use 'Cerrar Período' para finalizar el ciclo abierto
                [img]cerrar_periodo.png[/img]
                """,
                'imagenes': {
                    'fecha_periodo.png': './imagenes/ayuda/fecha_periodo.png',
                    'boton_crear_periodo.png': './imagenes/ayuda/boton_crear_periodo.png',
                    'historial_periodo.png': './imagenes/ayuda/historial_periodo.png',
                    'cerrar_periodo.png': './imagenes/ayuda/cerrar_periodo.png'
                }
            },
            'prestamos': {
                'titulo': 'Módulo de Préstamos',
                'contenido': """
                El módulo de préstamos permite gestionar los prestamos a los empleados:
                
                • Registro de nuevos préstamos
                • Control de cuotas y saldos
                • Estado de pagos
                
                Operaciones principales:
                1. Para registrar un nuevo préstamo, use el botón 'Nueva Solicitud'
                [img]boton_solicitar_prestamo.png[/img]
                [img]solicitar_prestamo.png[/img]
                2. Para aceptar o rechazar un prestamo, seleccionelo y use los botones 'Aprobar' o 'Rechazar' según el caso (Solo personal autorizado)
                [img]botones_prestamo.png[/img]
                2.1. En dado caso de rechazar ingresar el motivo
                [img]rechazar_prestamo.png[/img]
                3. Para ver el estado de un prestamo puede fijarse en el color y en la columna de estado
                [img]estado_prestamos.png[/img]
                4. Para ver los detalles de un prestamo use el botón 'Ver Detalles'
                [img]detalles_prestamo.png[/img]
                """,
                'imagenes': {
                    'boton_solicitar_prestamo.png': './imagenes/ayuda/boton_solicitar_prestamo.png',
                    'solicitar_prestamo.png': './imagenes/ayuda/solicitar_prestamo.png',
                    'botones_prestamo.png': './imagenes/ayuda/botones_prestamo.png',
                    'rechazar_prestamo.png': './imagenes/ayuda/rechazar_prestamo.png',
                    'estado_prestamos.png': './imagenes/ayuda/estado_prestamos.png',
                    'detalles_prestamo.png': './imagenes/ayuda/detalles_prestamo.png'
                }
            },
            'reportes': {
                'titulo': 'Módulo de Reportes',
                'contenido': """
                El módulo de reportes permite visualizar y gestionar recibos de pago:

                • Visualización de recibos por período
                • Acceso a histórico de pagos
                • Gestión de archivos generados

                Operaciones principales:

                1. Seleccione un período para ver sus reportes
                [img]seleccionar_periodo_reporte.png[/img]
                2. Use 'Abrir Reporte' para ver un recibo específico
                [img]abrir_reporte.png[/img]
                [img]reporte.png[/img]
                3. Use 'Abrir Carpeta' para acceder al directorio (Solo para usuarios autorizados)
                [img]abrir_carpeta_reporte.png[/img]
                [img]carpeta_reporte.png[/img]
                """,
                'imagenes': {
                    'seleccionar_periodo_reporte.png': './imagenes/ayuda/seleccionar_periodo_reporte.png',
                    'abrir_reporte.png': './imagenes/ayuda/abrir_reporte.png',
                    'reporte.png': './imagenes/ayuda/reporte.png',
                    'abrir_carpeta_reporte.png': './imagenes/ayuda/abrir_carpeta_reporte.png',
                    'carpeta_reporte.png': './imagenes/ayuda/carpeta_reporte.png'
                }
            },
            'mantenimiento': {
                'titulo': 'Módulo de Mantenimiento',
                'contenido': """
                El módulo de mantenimiento gestiona la integridad del sistema:
                (Solo está disponible para usuarios autorizados)

                • Respaldo de base de datos
                • Restauración de copias
                • Registro de las acciones

                Operaciones principales:

                1. Crear respaldo con 'Crear Respaldo'
                [img]crear_respaldo.png[/img]
                2. Restaurar usando 'Restaurar Respaldo'
                [img]restaurar_respaldo.png[/img]
                3. Para ver los registro use el botón 'Buscar' en pestaña Auditoría
                [img]buscar_auditoria.png[/img]
                """,
                'imagenes':{
                    'crear_respaldo.png': './imagenes/ayuda/crear_respaldo.png',
                    'restaurar_respaldo.png': './imagenes/ayuda/restaurar_respaldo.png',
                    'buscar_auditoria.png': './imagenes/ayuda/buscar_auditoria.png'
                }
            }
        }

    def mostrar_ayuda(self, contexto):
        """Muestra la ventana de ayuda para el contexto especificado"""
        ventana_ayuda = VentanaAyuda(self.contenido_ayuda.get(contexto, {}))

class VentanaAyuda(tk.Toplevel):
    def __init__(self, datos_ayuda):
        super().__init__()
        self.title("Ayuda del Sistema")
        self.geometry("800x600")

        # Notebook para pestañas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Pestaña de contenido general
        self.frame_general = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_general, text="Información General")

        # Canvas con scroll para el contenido
        self.canvas = tk.Canvas(self.frame_general)
        scrollbar = ttk.Scrollbar(self.frame_general, orient="vertical", command=self.canvas.yview)
        self.frame_contenido = ttk.Frame(self.canvas)
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.frame_contenido, anchor="nw")

        # Título
        ttk.Label(
            self.frame_contenido,
            text=datos_ayuda.get('titulo', 'Ayuda del Sistema'),
            font=('Helvetica', 12, 'bold')
        ).pack(pady=10, anchor='w')

        self.mostrar_contenido(datos_ayuda)
        
        # Configurar scroll
        self.frame_contenido.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind('<Configure>', self.frame_width)

        # Pestaña de atajos
        if datos_ayuda.get('atajos'):
            self.crear_pestana_atajos(datos_ayuda['atajos'])

    def mostrar_contenido(self, datos_ayuda):
        contenido = datos_ayuda.get('contenido', '')
        imagenes = datos_ayuda.get('imagenes', {})
        
        # Procesar el contenido
        partes = contenido.split('[img]')
        for i, parte in enumerate(partes):
            if i == 0:
                if parte.strip():
                    self.agregar_texto(parte)
                continue
                
            # Procesar imagen
            img_nombre = parte.split('[/img]')[0]
            if img_nombre in imagenes:
                self.agregar_imagen(imagenes[img_nombre])
            
            # Agregar texto después de la imagen
            texto_despues = parte.split('[/img]')[1]
            if texto_despues.strip():
                self.agregar_texto(texto_despues)

    def agregar_texto(self, texto):
        label = ttk.Label(self.frame_contenido, text=texto, wraplength=750)
        label.pack(padx=20, pady=5)

    def agregar_imagen(self, ruta_imagen):
        if os.path.exists(ruta_imagen):
            img = Image.open(ruta_imagen)
            # Redimensionar si es necesario
            if img.size[0] > 700:
                ratio = 700.0 / img.size[0]
                nuevo_alto = int(img.size[1] * ratio)
                img = img.resize((700, nuevo_alto), Image.Resampling.LANCZOS)
            
            foto = ImageTk.PhotoImage(img)
            label = ttk.Label(self.frame_contenido, image=foto)
            label.image = foto
            label.pack(padx=20, pady=5)

    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def frame_width(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width)

    def crear_pestana_atajos(self, atajos):
        frame_atajos = ttk.Frame(self.notebook)
        self.notebook.add(frame_atajos, text="Atajos de Teclado")
        
        ttk.Label(
            frame_atajos,
            text="Atajos disponibles:",
            font=('Helvetica', 11, 'bold')
        ).pack(pady=10, anchor='w')
        
        for atajo, descripcion in atajos.items():
            frame_atajo = ttk.Frame(frame_atajos)
            frame_atajo.pack(fill=tk.X, pady=2)
            
            ttk.Label(
                frame_atajo,
                text=f"{atajo}:",
                font=('Helvetica', 10, 'bold'),
                width=15
            ).pack(side=tk.LEFT, padx=5)
            
            ttk.Label(
                frame_atajo,
                text=descripcion,
                font=('Helvetica', 10)
            ).pack(side=tk.LEFT, padx=5)