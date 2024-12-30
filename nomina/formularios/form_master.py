import tkinter as tk
from tkinter import ttk, Menu, messagebox
from PIL import Image, ImageTk
from util.db_manager import DatabaseManager
from util.config import DB_CONFIG
from datetime import datetime

class MainApp(tk.Tk):
    def __init__(self, username=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.db_manager = DatabaseManager(**DB_CONFIG)
        
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

        # Cargar y mostrar el logo
        try:
            self.logo_image = Image.open("./imagenes/Logo RHG.jpg")
            self.logo_image = self.logo_image.resize((60, 60), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(self.logo_image)
            self.logo_label = ttk.Label(self.left_header, image=self.logo_photo)
            self.logo_label.pack(side=tk.LEFT, padx=10, pady=5)
        except:
            print("No se pudo cargar el logo")

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
        self.user_info_frame.pack(pady=5)

        # Mostrar información del usuario
        user_name = f"{self.user_data['nombre']} {self.user_data['apellido']}"
        ttk.Label(self.user_info_frame, text=user_name, 
                 style='User Bold.TLabel').pack(anchor='e')
        ttk.Label(self.user_info_frame, text=self.user_data['rol'], 
                 style='User .TLabel').pack(anchor='e')

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

    def crear_menu(self):
        """Crea el menú principal de la aplicación."""
        menubar = Menu(self)
        
        # Definir la estructura del menú
        self.menu_structure = {
            "Empleados": [
                ("Gestionar Empleados", self.empleados),
                ("Administrar NFC", self.nfc),
                ("Gestionar usuarios", self.gestionar_usuarios)
            ],
            "Nómina": [
                ("Generar Prenómina", self.mostrar_prenomina),
                ("Control de Asistencias", self.gestion_asistencia)
            ],
            "Periodos": [
                ("Gestionar Periodos", self.gestion_periodos)
            ],
            "Prestamos": [
                ("Gestionar Prestamo", self.gestionar_prestamo),
            ],
            "Reportes": [
                ("Ver Reportes", self.reportes)
            ],
            "Mantenimiento": [
                ("Mantenimiento del Sistema", self.mantenimiento)
            ]
        }

        # Crear el menú principal
        menu_bar = Menu(self)
        self.config(menu=menu_bar)

        # Agregar submenús al menú principal
        for menu_name, options in self.menu_structure.items():
            menu = Menu(menu_bar, tearoff=0)
            menu_bar.add_cascade(label=menu_name, menu=menu)
            
            # Agregar opciones a los submenús
            for option_text, command in options:
                menu.add_command(label=option_text, command=command)
        
        menu_bar.add_command(label="Cerrar Sesión", command=self.cerrar_sesion)

    def clear_main_frame(self):
        """Limpia el contenido del frame principal"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def mensaje(self):
        """Muestra la pantalla de bienvenida"""
        self.clear_main_frame()
        welcome_frame = ttk.Frame(self.main_frame)
        welcome_frame.pack(expand=True)
        
        ttk.Label(welcome_frame, text="Bienvenido al Sistema de Nómina", 
                 font=('Helvetica', 24)).pack(pady=20)
        ttk.Label(welcome_frame, text="Seleccione una opción del menú para comenzar", 
                 font=('Helvetica', 12)).pack()

    def empleados(self):
        """Muestra el módulo de gestión de empleados"""
        self.clear_main_frame()
        from formularios.empleados_form import EmpleadosForm
        EmpleadosForm(self.main_frame, self.db_manager)

    def gestionar_usuarios(self):
        """Muestra el módulo de gestión de usuarios"""
        self.clear_main_frame()
        from formularios.usuarios_form import GestionUsuariosForm
        GestionUsuariosForm(self.main_frame, self.db_manager)

    def nfc(self):
        """Muestra el módulo de administración NFC"""
        self.clear_main_frame()
        from formularios.nfc_form import NfcForm
        NfcForm(self.main_frame, self.db_manager)

    def mostrar_prenomina(self):
        """Muestra el módulo de prenómina"""
        self.clear_main_frame()
        from formularios.prenomina_form import PrenominaForm
        PrenominaForm(self.main_frame, self.db_manager)

    def gestion_asistencia(self):
        """Muestra el módulo de asistencias"""
        self.clear_main_frame()
        from formularios.asistencias_form import AsistenciasForm
        AsistenciasForm(self.main_frame, self.db_manager)

    def gestion_periodos(self):
        """Muestra el módulo de periodos"""
        self.clear_main_frame()
        from formularios.periodo_nomina_form import PeriodoNominaForm
        PeriodoNominaForm(self.main_frame, self.db_manager)

    def gestionar_prestamo(self):
        """Muestra el formulario para préstamo"""
        self.clear_main_frame()
        from formularios.prestamos_form import PrestamosForm
        PrestamosForm(self.main_frame, self.db_manager, self.user_data)

    def reportes(self):
        """Muestra el módulo de reportes"""
        self.clear_main_frame()
        from formularios.reportes_form import ReportesForm
        ReportesForm(self.main_frame, self.db_manager)

    def mantenimiento(self):
        """Muestra el módulo de mantenimiento"""
        self.clear_main_frame()
        from formularios.mantenimiento_form import MantenimientoForm
        MantenimientoForm(self.main_frame, self.db_manager)

    def actualizar_fecha(self):
        """Actualiza la fecha y hora en tiempo real"""
        now = datetime.now()
        date_str = now.strftime("%d/%m/%Y")
        time_str = now.strftime("%H:%M:%S")
        
        self.date_label.config(text=date_str)
        self.time_label.config(text=time_str)
        
        # Store after id for cleanup
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
            self.destroy()
            from formularios.form_login import LoginForm
            login = LoginForm()
            login.mainloop

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()