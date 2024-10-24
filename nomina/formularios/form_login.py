import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from util.db_manager import DatabaseManager
from util.config import DB_CONFIG
from formularios.form_master import MainApp  # Importa la clase MainApp

class LoginForm(tk.Tk):
    def __init__(self):
        super().__init__()

        self.is_logged_in = False
        self.username = ""

        # Inicializar el manager con la configuración
        self.db_manager = DatabaseManager(**DB_CONFIG)

        # Configuración de la ventana
        self.title("Inicio de Sesión - Sistema de Nómina R.H.G Inversiones, C.A.") 
        self.geometry("400x500")

        # Frame principal
        self.frame = tk.Frame(self)
        self.frame.pack(pady=20, padx=40, fill="both", expand=True)

        # Frame blanco para el logo
        self.logo_frame = tk.Frame(self.frame, bg="white")
        self.logo_frame.pack(pady=5, padx=0, fill="x")

        # Logo
        self.logo_image = Image.open("./imagenes/logo.png")
        self.logo_image = self.logo_image.resize((150, 150), Image.ADAPTIVE)
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self.logo_frame, image=self.logo_photo, bg="white")
        self.logo_label.pack(pady=10, padx=10)

        # Título
        self.label = tk.Label(self.frame, text="Inicio de Sesión", font=("Roboto", 24))
        self.label.pack(pady=10, padx=10)

        # Label para mostrar mensajes de error (Dentro del frame)
        self.error_label = tk.Label(self.frame, text="", fg="red")
        self.error_label.pack(pady=5)

        # Campo de usuario
        self.user_entry = tk.Entry(self.frame)
        self.user_entry.insert(0, "admin")
        self.user_entry.pack(pady=10, padx=10)

        # Campo de contraseña
        self.password_entry = tk.Entry(self.frame, show="*")
        self.password_entry.insert(0, "admin")
        self.password_entry.pack(pady=10, padx=10)

        # Botón de inicio de sesión
        self.login_button = tk.Button(self.frame, text="Iniciar Sesión", command=self.login)
        self.login_button.pack(pady=10, padx=10)

        # Botón de salir
        self.exit_button = tk.Button(self.frame, text="Salir", command=self.exit)
        self.exit_button.pack(pady=10, padx=10)

    def login(self):
        username = self.user_entry.get()
        password = self.password_entry.get()

        if self.db_manager.verify_credentials(username, password):
            self.error_label.config(text="")  # Limpia el error si es exitoso
            self.quit()  # Cierra el formulario de inicio de sesión
            self.open_main_app()  # Abre la aplicación principal
        else:
            self.error_label.config(text="Usuario o contraseña incorrectos")

    def exit(self):
        self.is_logged_in = False
        self.quit()

    def open_main_app(self):
        # Instancia la clase MainApp y abre la ventana principal
        self.quit()
        self.destroy()  # Cierra la ventana de inicio de sesión
        main_app = MainApp()  # Crea la nueva ventana
        main_app.mainloop()  # Inicia el mainloop() para la ventana principal

if __name__ == "__main__":
    app = LoginForm()
    app.mainloop()
