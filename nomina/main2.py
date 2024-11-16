import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from util.db_manager import DatabaseManager
from util.config import DB_CONFIG
from datetime import datetime

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.db_manager = DatabaseManager(**DB_CONFIG)

        # Configuración básica de la ventana principal
        self.title("Sistema de Nómina - R.H.G Inversiones, C.A.")
        self.geometry("1200x700")
        
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
            self.logo_image = Image.open("./imagenes/logo.png")
            self.logo_image = self.logo_image.resize((60, 60), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(self.logo_image)
            self.logo_label = ttk.Label(self.left_header, image=self.logo_photo)
            self.logo_label.pack(side=tk.LEFT, padx=10, pady=5)
        except:
            print("No se pudo cargar el logo")

        # Título de la aplicación
        title_frame = ttk.Frame(self.left_header)
        title_frame.pack(side=tk.LEFT, padx=10)
        ttk.Label(title_frame, text="Sistema de Nómina", 
                 font=('Helvetica', 20, 'bold')).pack()
        ttk.Label(title_frame, text="R.H.G Inversiones, C.A.", 
                 font=('Helvetica', 12)).pack()

        # Frame derecho para información del usuario
        self.right_header = ttk.Frame(self.header_frame)
        self.right_header.pack(side=tk.RIGHT, padx=20)

        # Estilo para la información del usuario
        style = ttk.Style()
        style.configure('User.TLabel', font=('Helvetica', 10))
        style.configure('UserBold.TLabel', font=('Helvetica', 10, 'bold'))
        style.configure('Time.TLabel', font=('Helvetica', 9))

        # Frame para la información del usuario
        self.user_info_frame = ttk.Frame(self.right_header)
        self.user_info_frame.pack(pady=5)

        # Información del usuario (esto deberías obtenerlo de tu sistema de autenticación)
        self.user_data = {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'rol': 'Administrador'
        }

        # Mostrar información del usuario
        user_name = f"{self.user_data['nombre']} {self.user_data['apellido']}"
        ttk.Label(self.user_info_frame, text=user_name, 
                 style='UserBold.TLabel').pack(anchor='e')
        ttk.Label(self.user_info_frame, text=self.user_data['rol'], 
                 style='User.TLabel').pack(anchor='e')
        
        # Labels para fecha y hora
        self.date_label = ttk.Label(self.user_info_frame, style='Time.TLabel')
        self.date_label.pack(anchor='e')
        self.time_label = ttk.Label(self.user_info_frame, style='Time.TLabel')
        self.time_label.pack(anchor='e')
        
        # Actualizar fecha y hora
        self.update_datetime()

        # Separador después del header
        ttk.Separator(self.main_container, orient='horizontal').pack(fill=tk.X, pady=5)

        # Frame para la barra de menú principal
        self.menu_frame = ttk.Frame(self.main_container)
        self.menu_frame.pack(fill=tk.X)

        # Estilo para los botones del menú
        style = ttk.Style()
        style.configure('MenuButton.TButton', font=('Helvetica', 10))
        
        # Crear los menús principales
        self.menu_buttons = {}
        self.submenus = {}
        
        # Definir la estructura del menú
        self.menu_structure = {
            "Empleados": [
                ("Gestionar Empleados", self.show_empleados),
                ("Administrar NFC", self.show_nfc)
            ],
            "Nómina": [
                ("Generar Prenómina", self.show_prenomina),
                ("Control de Asistencias", self.show_asistencias)
            ],
            "Periodos": [
                ("Gestionar Periodos", self.show_periodos)
            ],
            "Reportes": [
                ("Ver Reportes", self.show_reportes)
            ]
        }

        # Crear los botones del menú principal y sus submenús
        for i, (menu_name, options) in enumerate(self.menu_structure.items()):
            # Crear frame para el menú desplegable
            menu_container = ttk.Frame(self.menu_frame)
            menu_container.pack(side=tk.LEFT, padx=5)
            
            # Botón principal del menú
            self.menu_buttons[menu_name] = ttk.Button(
                menu_container,
                text=menu_name,
                style='MenuButton.TButton',
                width=15
            )
            self.menu_buttons[menu_name].pack()

            # Crear el submenú (inicialmente oculto)
            submenu = tk.Frame(self.main_container, relief="raised", borderwidth=1)
            self.submenus[menu_name] = submenu

            # Agregar opciones al submenú
            for option_text, command in options:
                btn = ttk.Button(submenu, text=option_text, command=command, width=20)
                btn.pack(fill=tk.X, padx=2, pady=1)

            # Configurar eventos para mostrar/ocultar submenú
            def show_submenu(menu_name):
                def _show(event):
                    # Ocultar todos los submenús primero
                    for submenu in self.submenus.values():
                        submenu.place_forget()
                    
                    # Mostrar el submenú actual
                    button = self.menu_buttons[menu_name]
                    x = button.winfo_rootx() - self.winfo_rootx()
                    y = button.winfo_rooty() - self.winfo_rooty() + button.winfo_height()
                    self.submenus[menu_name].place(x=x, y=y)
                return _show

            def hide_submenu(menu_name):
                def _hide(event):
                    # No ocultar inmediatamente para permitir clic en opciones
                    self.after(100, lambda: self.check_mouse_position(menu_name))
                return _hide

            self.menu_buttons[menu_name].bind('<Enter>', show_submenu(menu_name))
            self.menu_buttons[menu_name].bind('<Leave>', hide_submenu(menu_name))
            submenu.bind('<Enter>', lambda e, m=menu_name: self.keep_submenu(m))
            submenu.bind('<Leave>', lambda e, m=menu_name: self.hide_current_submenu(m))

        # Separador después del menú
        ttk.Separator(self.main_container, orient='horizontal').pack(fill=tk.X, pady=5)

        # Frame principal para el contenido
        self.main_frame = ttk.Frame(self.main_container)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Frame de bienvenida inicial
        self.show_welcome()

    def check_mouse_position(self, menu_name):
        """Verifica si el mouse está sobre el submenú antes de ocultarlo"""
        submenu = self.submenus[menu_name]
        mouse_x = self.winfo_pointerx() - self.winfo_rootx()
        mouse_y = self.winfo_pointery() - self.winfo_rooty()
        
        submenu_x = submenu.winfo_x()
        submenu_y = submenu.winfo_y()
        submenu_width = submenu.winfo_width()
        submenu_height = submenu.winfo_height()
        
        if not (submenu_x <= mouse_x <= submenu_x + submenu_width and 
                submenu_y <= mouse_y <= submenu_y + submenu_height):
            submenu.place_forget()

    def keep_submenu(self, menu_name):
        """Mantiene visible el submenú cuando el mouse está sobre él"""
        pass  # El menú ya está visible

    def hide_current_submenu(self, menu_name):
        """Oculta el submenú actual"""
        self.submenus[menu_name].place_forget()

    def clear_main_frame(self):
        """Limpia el contenido del frame principal"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_welcome(self):
        """Muestra la pantalla de bienvenida"""
        self.clear_main_frame()
        welcome_frame = ttk.Frame(self.main_frame)
        welcome_frame.pack(expand=True)
        
        ttk.Label(welcome_frame, text="Bienvenido al Sistema de Nómina", 
                 font=('Helvetica', 24)).pack(pady=20)
        ttk.Label(welcome_frame, text="Seleccione una opción del menú para comenzar", 
                 font=('Helvetica', 12)).pack()

    def show_empleados(self):
        """Muestra el módulo de gestión de empleados"""
        self.clear_main_frame()
        from formularios.empleados_form import EmpleadosForm
        EmpleadosForm(self.main_frame, self.db_manager)

    def show_nfc(self):
        """Muestra el módulo de administración NFC"""
        self.clear_main_frame()
        from formularios.nfc_form import NfcForm
        NfcForm(self.main_frame, self.db_manager)

    def show_prenomina(self):
        """Muestra el módulo de prenómina"""
        self.clear_main_frame()
        from formularios.prenomina_form import PrenominaForm
        PrenominaForm(self.main_frame, self.db_manager)

    def show_asistencias(self):
        """Muestra el módulo de asistencias"""
        self.clear_main_frame()
        from formularios.asistencias_form import AsistenciasForm
        AsistenciasForm(self.main_frame, self.db_manager)

    def show_periodos(self):
        """Muestra el módulo de periodos"""
        self.clear_main_frame()
        from formularios.periodo_nomina_form import PeriodoNominaForm
        PeriodoNominaForm(self.main_frame, self.db_manager)

    def show_reportes(self):
        """Muestra el módulo de reportes"""
        self.clear_main_frame()
        from formularios.reportes_form import ReportesForm
        ReportesForm(self.main_frame, self.db_manager)


    def update_datetime(self):
        """Actualiza la fecha y hora en tiempo real"""
        now = datetime.now()
        date_str = now.strftime("%d/%m/%Y")
        time_str = now.strftime("%H:%M:%S")
        
        self.date_label.config(text=date_str)
        self.time_label.config(text=time_str)
        
        # Actualizar cada segundo
        self.after(1000, self.update_datetime)

    # Método para actualizar la información del usuario
    def update_user_info(self, user_data):
        """
        Actualiza la información del usuario mostrada
        user_data debe ser un diccionario con 'nombre', 'apellido' y 'rol'
        """
        self.user_data = user_data
        user_name = f"{user_data['nombre']} {user_data['apellido']}"
        
        # Actualizar las etiquetas
        self.user_info_frame.winfo_children()[0].config(text=user_name)
        self.user_info_frame.winfo_children()[1].config(text=user_data['rol'])
if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()