import tkinter as tk
from tkinter import ttk, Menu, messagebox
from PIL import Image, ImageTk
from util.db_manager import DatabaseManager
from util.config import DB_CONFIG
from util.notification_manager import NotificationManager
from datetime import datetime
from ttkthemes import ThemedStyle

class NotificationPopup(tk.Toplevel):
    def __init__(self, parent, notificaciones, notification_manager):
        super().__init__(parent)
        self.notification_manager = notification_manager
        
        # Configuración de la ventana
        self.title("Notificaciones")
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Frame principal
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header con contador y botón de marcar todo como leído
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text=f"Notificaciones ({len(notificaciones)})", 
                 font=('Helvetica', 12, 'bold')).pack(side=tk.LEFT)
        
        if notificaciones:
            ttk.Button(header_frame, text="Marcar todas como leídas",
                      command=self.marcar_todas_leidas).pack(side=tk.RIGHT)
        
        # Frame para la lista de notificaciones con scroll
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas y scrollbar para el scroll
        self.canvas = tk.Canvas(list_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", 
                                command=self.canvas.yview)
        
        # Frame dentro del canvas para las notificaciones
        self.notification_frame = ttk.Frame(self.canvas)
        
        # Configurar scrolling
        self.notification_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Crear ventana en el canvas
        self.canvas.create_window((0, 0), window=self.notification_frame, 
                                anchor="nw", width=380)
        
        # Configurar scrollbar
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configurar bindings para el scroll
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.bind("<Destroy>", lambda e: self.canvas.unbind_all("<MouseWheel>"))
        
        # Pack elementos
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mostrar notificaciones
        self.mostrar_notificaciones(notificaciones)
        
        # Hacer la ventana modal
        self.transient(parent)
        self.grab_set()
        
        # Centrar la ventana
        self.center_window()
    
    def _on_mousewheel(self, event):
        """Manejar el evento del scroll del mouse"""
        self.canvas.yview_scroll(int(-1 * (event.delta/120)), "units")
        
    def mostrar_notificaciones(self, notificaciones):
        if not notificaciones:
            ttk.Label(self.notification_frame, 
                     text="No hay notificaciones nuevas",
                     font=('Helvetica', 10)).pack(pady=20)
            return
            
        for notif in notificaciones:
            self.crear_notificacion_widget(notif)
            
    def crear_notificacion_widget(self, notif):
        # Frame para cada notificación
        notif_frame = ttk.Frame(self.notification_frame)
        notif_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Contenido de la notificación
        content_frame = ttk.Frame(notif_frame)
        content_frame.pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        # Título/Tipo
        tipo_label = ttk.Label(content_frame, 
                             text=notif['tipo'].capitalize(),
                             font=('Helvetica', 9, 'bold'))
        tipo_label.pack(anchor='w')
        
        # Mensaje
        mensaje_label = ttk.Label(content_frame, 
                                text=notif['mensaje'],
                                wraplength=300)
        mensaje_label.pack(anchor='w')
        
        # Fecha
        fecha = notif['fecha_generacion'].strftime("%d/%m/%Y %H:%M")
        fecha_label = ttk.Label(content_frame,
                              text=fecha,
                              font=('Helvetica', 8),
                              foreground='gray')
        fecha_label.pack(anchor='w')
        
        # Separador
        ttk.Separator(self.notification_frame, 
                     orient='horizontal').pack(fill=tk.X, pady=5)
        
        # Si no está leída, añadir botón de marcar como leída
        if notif['estado'] == 'no_leida':
            ttk.Button(notif_frame,
                      text="✓",
                      width=3,
                      command=lambda: self.marcar_leida(notif['id_notificacion']),
                      ).pack(side=tk.RIGHT, padx=5)
            
    def marcar_leida(self, id_notificacion):
        """Marcar una notificación específica como leída"""
        if self.notification_manager.marcar_como_leida(id_notificacion):
            # Actualizar la interfaz
            self.master.verificar_notificaciones()
            self.destroy()
            
    def marcar_todas_leidas(self):
        """Marcar todas las notificaciones como leídas"""
        if self.notification_manager.marcar_todas_como_leidas(
                self.master.user_data['id_usuario']):
            self.master.verificar_notificaciones()
            self.destroy()
            
    def center_window(self):
        """Centrar la ventana en la pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

class MainApp(tk.Tk):
    def __init__(self, username=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.db_manager = DatabaseManager(**DB_CONFIG)
        self.configurar_estilos()
        
        # Cargar información del usuario que inició sesión
        self.username = username
        self.user_data = self.cargar_datos_usuario()

        # Configuración básica de la ventana principal
        self.title("NomiInversiones - R.H.G Inversiones, C.A.")
        self.geometry("1200x700")

        # Crear el menú
        self.crear_menu()

        # Crear el contenedor principal
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Frame para el header con logo, título e información de usuario
        self.header_frame = ttk.Frame(self.main_container)
        self.header_frame.pack(fill=tk.X)

        # Frame izquierdo para logo y título
        self.left_header = ttk.Frame(self.header_frame)
        self.left_header.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Frame para la campana y contador
        self.notification_frame = ttk.Frame(self.header_frame)
        self.notification_frame.pack(side=tk.LEFT, padx=10, pady=10)

        # Cargar y mostrar el logo
        try:
            self.logo_image = Image.open("./imagenes/Logo RHG.jpg")
            self.logo_image = self.logo_image.resize((60, 60), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(self.logo_image)
            self.logo_label = ttk.Label(self.left_header, image=self.logo_photo)
            self.logo_label.pack(side=tk.LEFT, padx=10, pady=5)
        except:
            print("No se pudo cargar el logo")

        self.logo_label.bind('<Button-1>', lambda e: self.mensaje())
        self.logo_label.bind('<Enter>', lambda e: self.logo_label.configure(cursor='hand2'))

        # Título de la aplicación
        title_frame = ttk.Frame(self.left_header)
        title_frame.pack(side=tk.LEFT, padx=10)
        ttk.Label(title_frame, text="NomiInversiones", 
                 font=('Helvetica', 20, 'bold')).pack()
        ttk.Label(title_frame, text="R.H.G Inversiones, C.A.", 
                 font=('Helvetica', 12)).pack()

        # Frame derecho para información del usuario
        self.right_header = ttk.Frame(self.header_frame)
        self.right_header.pack(side=tk.RIGHT, padx=20)

        # Estilo para la información del usuario
        style = ttk.Style()
        style.configure('User .TLabel', font=('Helvetica', 10))
        style.configure('User Bold.TLabel', font=('Helvetica', 10, 'bold'))
        style.configure('Time.TLabel', font=('Helvetica', 9))

        # Frame para la información del usuario
        self.user_info_frame = ttk.Frame(self.right_header)
        self.user_info_frame.pack(side=tk.RIGHT, pady=5)

        # Frame para la campana y contador
        self.notification_frame = ttk.Frame(self.right_header)
        self.notification_frame.pack(side=tk.RIGHT, padx=(0, 10))

        # Mostrar información del usuario
        user_name = f"{self.user_data['nombre']} {self.user_data['apellido']}"
        ttk.Label(self.user_info_frame, text=user_name, 
                 style='User Bold.TLabel').pack(anchor='e')
        ttk.Label(self.user_info_frame, text=self.user_data['rol'], 
                 style='User .TLabel').pack(anchor='e')
        
        # Inicializar NotificationManager
        self.notification_manager = NotificationManager(self.db_manager)
                
        # Cargar icono de campana
        try:
            bell_img = Image.open("./imagenes/bell-icon.png")  # Asegúrate de tener este ícono
            bell_img = bell_img.resize((20, 20), Image.Resampling.LANCZOS)
            self.bell_photo = ImageTk.PhotoImage(bell_img)
        except:
            # Si no se puede cargar la imagen, usar texto
            self.bell_photo = None
        
        # Botón de campana
        self.bell_button = tk.Button(
            self.notification_frame,
            image=self.bell_photo if self.bell_photo else None,
            text="🔔" if not self.bell_photo else "",  # Emoji como respaldo
            bd=0,
            bg='white',
            cursor='hand2',
            command=self.mostrar_notificaciones
        )
        self.bell_button.pack(side=tk.LEFT, pady=(5,0))
        
        # Contador de notificaciones
        self.notification_count = tk.Label(
            self.notification_frame,
            text="0",
            bg='red',
            fg='white',
            font=('Helvetica', 8),
            width=2,
            height=1,
            borderwidth=0
        )
        
        # Iniciar verificación de notificaciones
        self.verificar_notificaciones()
        
        # Programar verificación periódica
        self.after(300000, self.verificar_notificaciones)  # Cada 5 minutos

        # Labels para fecha y hora
        self.date_label = ttk.Label(self.user_info_frame, style='Time.TLabel')
        self.date_label.pack(anchor='e')
        self.time_label = ttk.Label(self.user_info_frame, style='Time.TLabel')
        self.time_label.pack(anchor='e')

        # Actualizar fecha y hora
        self.actualizar_fecha()

        # Separador después del header
        ttk.Separator(self.main_container, orient='horizontal').pack(fill=tk.X, pady=5)

        # Frame principal para el contenido
        self.main_frame = ttk.Frame(self.main_container)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Frame de bienvenida inicial
        self.mensaje()

        self.center_window()

    def configurar_estilos(self):
        style = ThemedStyle(self)
        self.tk.call("source", "./awthemes/awlight.tcl")
        style.theme_use('awlight')  # Tema
        
        # Colores principales
        style.configure('.',
            background='#f8fafc',
            foreground='#1e293b',
            font=('Helvetica', 10)
        )
        
        # Header
        style.configure('Header.TFrame', 
            background='#ffffff',
            relief='flat'
        )
        
        # Botones
        style.configure('Primary.TButton',
            background='#2563eb',
            foreground='white',
            padding=(10, 5),
            font=('Helvetica', 10, 'bold')
        )
        
        style.map('Primary.TButton',
            background=[('active', '#1d4ed8')],
            foreground=[('active', 'white')]
        )
        
        # Labels
        style.configure('Title.TLabel',
            font=('Helvetica', 20, 'bold'),
            foreground='#1e293b'
        )
        
        style.configure('Subtitle.TLabel',
            font=('Helvetica', 12),
            foreground='#64748b'
        )

    def crear_menu(self):
        menubar = Menu(self)
        
        # Estructura del menú con los permisos requeridos
        self.menu_structure = {
            "Empleados": [
                ("Gestionar Empleados", self.empleados, "empleados.gestion"),
                ("Administrar NFC", self.nfc, "empleados.nfc"),
                ("Gestionar usuarios", self.gestionar_usuarios, "empleados.usuarios")
            ],
            "Nómina": [
                ("Generar Prenómina", self.mostrar_prenomina, "nomina.prenomina"),
                ("Control de Asistencias", self.gestion_asistencia, "nomina.asistencias")
            ],
            "Periodos": [
                ("Gestionar Periodos", self.gestion_periodos, "periodos.gestion")
            ],
            "Préstamos": [
                ("Gestionar Préstamo", self.gestionar_prestamo, "prestamos.gestion")
            ],
            "Reportes": [
                ("Ver Reportes", self.reportes, "reportes.ver")
            ],
            "Mantenimiento": [
                ("Mantenimiento del Sistema", self.mantenimiento, "mantenimiento.gestion"),
                ("Gestión de Porcentajes", self.gestionar_porcentajes, "mantenimiento.gestion")
            ]
        }

        menu_bar = Menu(self)
        self.config(menu=menu_bar)

        # Agregar submenús
        for menu_name, options in self.menu_structure.items():
            menu = Menu(menu_bar, tearoff=0)
            alguna_opcion_habilitada = False

            for option_text, command, permiso in options:
                tiene_permiso = self.db_manager.verificar_permiso(
                    self.user_data['id_usuario'],
                    permiso
                )
                
                if tiene_permiso:
                    menu.add_command(label=option_text, command=command)
                    alguna_opcion_habilitada = True
                else:
                    menu.add_command(label=option_text, command=command, state='disabled')

            if alguna_opcion_habilitada:
                menu_bar.add_cascade(label=menu_name, menu=menu)

        menu_bar.add_command(label="Cerrar Sesión", command=self.cerrar_sesion)

    def clear_main_frame(self):
        """Limpia el contenido del frame principal"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def mensaje(self):
        """Muestra la pantalla de bienvenida"""
        self.clear_main_frame()
        
        # Frame central para todo el contenido
        center_frame = ttk.Frame(self.main_frame)
        center_frame.pack(expand=True)
        
        try:
            # Cargar y mostrar el logo grande
            logo_img = Image.open("./imagenes/logo.png")
            logo_img = logo_img.resize((300, 300), Image.Resampling.LANCZOS)
            self.home_logo = ImageTk.PhotoImage(logo_img)
            
            logo_label = ttk.Label(center_frame, image=self.home_logo)
            logo_label.pack(pady=20)
        except Exception as e:
            print(f"Error al cargar el logo del home: {e}")
        
        # Mensajes de bienvenida
        ttk.Label(
            center_frame, 
            text="Bienvenido a NomiInversiones",
            font=('Helvetica', 24, 'bold')
        ).pack(pady=(0, 10))
        
        ttk.Label(
            center_frame,
            text="Trabajando juntos por el crecimiento de nuestra empresa",
            font=('Helvetica', 14),
            foreground='#666666'
        ).pack()

    def empleados(self):
        """Muestra el módulo de gestión de empleados"""
        self.clear_main_frame()
        from formularios.empleados_form import EmpleadosForm
        EmpleadosForm(self.main_frame, self.db_manager, self.user_data)

    def gestionar_usuarios(self):
        """Muestra el módulo de gestión de usuarios"""
        self.clear_main_frame()
        from formularios.usuarios_form import GestionUsuariosForm
        GestionUsuariosForm(self.main_frame, self.db_manager, self.user_data)

    def nfc(self):
        """Muestra el módulo de administración NFC"""
        self.clear_main_frame()
        from formularios.nfc_form import NfcForm
        NfcForm(self.main_frame, self.db_manager, self.user_data)

    def mostrar_prenomina(self):
        """Muestra el módulo de prenómina"""
        self.clear_main_frame()
        from formularios.prenomina_form import PrenominaForm
        PrenominaForm(self.main_frame, self.db_manager, self.user_data)

    def gestion_asistencia(self):
        """Muestra el módulo de asistencias"""
        self.clear_main_frame()
        from formularios.asistencias_form import AsistenciasForm
        AsistenciasForm(self.main_frame, self.db_manager, self.user_data)

    def gestion_periodos(self):
        """Muestra el módulo de periodos"""
        self.clear_main_frame()
        from formularios.periodo_nomina_form import PeriodoNominaForm
        PeriodoNominaForm(self.main_frame, self.db_manager, self.user_data)

    def gestionar_prestamo(self):
        """Muestra el formulario para préstamo"""
        self.clear_main_frame()
        from formularios.prestamos_form import PrestamosForm
        PrestamosForm(self.main_frame, self.db_manager, self.user_data)

    def reportes(self):
        """Muestra el módulo de reportes"""
        self.clear_main_frame()
        from formularios.reportes_form import ReportesForm
        ReportesForm(self.main_frame, self.db_manager, self.user_data)

    def mantenimiento(self):
        """Muestra el módulo de mantenimiento"""
        self.clear_main_frame()
        from formularios.mantenimiento_form import MantenimientoForm
        MantenimientoForm(self.main_frame, self.db_manager, self.user_data)

    def gestionar_porcentajes(self):
        """Muestra el formulario de porcentajes para bonos y deducciones"""
        self.clear_main_frame()
        from formularios.porcentajes_form import GestionPorcentajesForm
        GestionPorcentajesForm(self.main_frame, self.db_manager, self.user_data)

    def actualizar_fecha(self):
        """Actualiza la fecha y hora en tiempo real"""
        now = datetime.now()
        date_str = now.strftime("%d/%m/%Y")
        time_str = now.strftime("%H:%M:%S")
        
        self.date_label.config(text=date_str)
        self.time_label.config(text=time_str)
        
        if not hasattr(self, 'after_ids'):
            self.after_ids = []
        after_id = self.after(1000, self.actualizar_fecha)
        self.after_ids.append(after_id)

    # Método para actualizar la información del usuario

    def cargar_datos_usuario(self):
        """Carga los datos del usuario desde la base de datos"""
        if not self.username:
            return {
                'nombre': 'Usuario',
                'apellido': 'Desconocido',
                'rol': 'Sin Rol'
            }

        query = """
        SELECT 
            e.nombre,
            e.apellido,
            u.rol,
            u.id_usuario,
            e.id_empleado
        FROM usuarios u
        JOIN empleados e ON u.id_empleado = e.id_empleado
        WHERE u.usuario = %s
        """
        
        try:
            result = self.db_manager.ejecutar_query(query, (self.username,), fetchone=True)
            if result:
                return {
                    'nombre': result[0],
                    'apellido': result[1],
                    'rol': result[2],
                    'id_usuario': result[3],
                    'id_empleado': result[4]
                }
            return {
                'nombre': 'Usuario',
                'apellido': 'Desconocido',
                'rol': 'Sin Rol'
            }
        except Exception as e:
            print(f"Error al cargar datos del usuario: {e}")
            return {
                'nombre': 'Error',
                'apellido': 'de Carga',
                'rol': 'Error'
            }
        
    def verificar_notificaciones(self):
            """Verificar y actualizar el contador de notificaciones"""
            if not hasattr(self, 'user_data') or 'id_usuario' not in self.user_data:
                return
                
            # Verificar y crear nuevas notificaciones
            self.notification_manager.verificar_y_crear_notificaciones(
                self.user_data['id_usuario']
            )
            
            # Contar notificaciones no leídas
            count = self.notification_manager.contar_notificaciones_no_leidas(
                self.user_data['id_usuario']
            )
            
            # Actualizar contador visual
            if count > 0:
                self.notification_count.config(text=str(count))
                self.notification_count.pack(side=tk.RIGHT)
            else:
                self.notification_count.pack_forget()
            
            # Programar siguiente verificación
            if not hasattr(self, 'after_ids'):
                self.after_ids = []
            after_id = self.after(300000, self.verificar_notificaciones)  # 5 minutos
            self.after_ids.append(after_id)
        
    def mostrar_notificaciones(self):
        """Mostrar ventana de notificaciones"""
        if not hasattr(self, 'user_data') or 'id_usuario' not in self.user_data:
            return
            
        # Obtener notificaciones
        notificaciones = self.notification_manager.obtener_notificaciones_usuario(
            self.user_data['id_usuario']
        )
        
        # Mostrar ventana de notificaciones
        NotificationPopup(self, notificaciones, self.notification_manager)

    def update_user_info(self):
        """Actualiza la información mostrada del usuario"""
        user_name = f"{self.user_data['nombre']} {self.user_data['apellido']}"
        
        # Actualizar las etiquetas
        self.user_info_frame.winfo_children()[0].config(text=user_name)
        self.user_info_frame.winfo_children()[1].config(text=self.user_data['rol'])

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def destroy(self):
        for after_id in self.after_ids:
            self.after_cancel(after_id)
        super().destroy()

    def cerrar_sesion(self):
        if messagebox.askyesno("Confirmar", "¿Está seguro que desea cerrar sesión?"):
            # Registrar cierre de sesión
            self.db_manager.registrar_auditoria(
                usuario=f"{self.user_data['nombre']} {self.user_data['apellido']}",
                rol=f"{self.user_data['rol']}",
                accion='Cerró Sesión',
                tabla='usuarios',
                detalle=f"Cierre de sesión desde la aplicación"
            )
            self.destroy()
            from formularios.form_login import LoginForm
            login = LoginForm()
            login.mainloop

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()