import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from util.db_manager import DatabaseManager
from util.config import DB_CONFIG
from formularios.form_master import MainApp  # Importa la clase MainApp
from main2 import MainWindow  # Importa la clase MainApp

class CambioClaveForm(tk.Toplevel):
    def __init__(self, parent, db_manager, usuario):
        super().__init__(parent)
        self.db_manager = db_manager
        self.usuario = usuario
        
        # Configuración de la ventana
        self.title("Cambio de Contraseña")
        self.geometry("400x300")
        
        # Frame principal
        frame = ttk.Frame(self, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Mensaje
        ttk.Label(frame, text="Por seguridad, debe cambiar su contraseña", 
                 wraplength=300).pack(pady=10)
        
        # Nueva contraseña
        ttk.Label(frame, text="Nueva contraseña:").pack(pady=5)
        self.nueva_clave = ttk.Entry(frame, show="*")
        self.nueva_clave.pack(pady=5)
        
        # Confirmar contraseña
        ttk.Label(frame, text="Confirmar contraseña:").pack(pady=5)
        self.confirmar_clave = ttk.Entry(frame, show="*")
        self.confirmar_clave.pack(pady=5)
        
        # Botón confirmar
        ttk.Button(frame, text="Confirmar", 
                  command=self.cambiar_clave).pack(pady=20)
        
        # No permitir cerrar la ventana
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Modal
        self.grab_set()
        self.transient(parent)
    
    def cambiar_clave(self):
        nueva = self.nueva_clave.get()
        confirmar = self.confirmar_clave.get()
        
        if not nueva or not confirmar:
            messagebox.showwarning("Advertencia", 
                                 "Por favor complete todos los campos")
            return
            
        if nueva != confirmar:
            messagebox.showwarning("Advertencia", 
                                 "Las contraseñas no coinciden")
            return
            
        if len(nueva) < 6:
            messagebox.showwarning("Advertencia", 
                                 "La contraseña debe tener al menos 6 caracteres")
            return
            
        # Cambiar contraseña
        if self.db_manager.cambiar_contraseña(self.usuario, nueva):
            messagebox.showinfo("Éxito", 
                              "Contraseña cambiada correctamente")
            self.destroy()
        else:
            messagebox.showerror("Error", 
                               "Error al cambiar la contraseña")


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
            # Verificar primer ingreso
            primer_ingreso, permisos = self.db_manager.verificar_primer_ingreso(username)
            
            if primer_ingreso:
                # Mostrar formulario de cambio de contraseña
                cambio_form = CambioClaveForm(self, self.db_manager, username)
                self.wait_window(cambio_form)
            
            self.username = username
            self.permisos = permisos
            self.is_logged_in = True
            self.quit()
            self.open_main_app()
        else:
            self.error_label.config(text="Usuario o contraseña incorrectos")

    def exit(self):
        self.is_logged_in = False
        self.quit()

    def open_main_app(self):
        # Instancia la clase MainApp y abre la ventana principal
        self.quit()
        self.destroy()  # Cierra la ventana de inicio de sesión
        main_app = MainWindow()  # Crea la nueva ventana
        main_app.mainloop()  # Inicia el mainloop() para la ventana principal

if __name__ == "__main__":
    app = LoginForm()
    app.mainloop()
