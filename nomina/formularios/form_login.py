import tkinter as tk
import bcrypt
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from util.db_manager import DatabaseManager
from util.config import DB_CONFIG
from formularios.form_master import MainApp
from tkinter.ttk import Combobox

class CambioClaveForm(tk.Toplevel):
    def __init__(self, parent, db_manager, usuario):
        super().__init__(parent)
        self.db_manager = db_manager
        self.usuario = usuario
        
        self.title("Configuración Inicial")
        self.configure(bg="#f0f0f0")
        
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(
            main_frame,
            text="Cambio de clave y pregunta de seguridad",
            style="Title.TLabel"
        )
        title_label.pack(pady=(0, 20))

        # Campos para contraseña
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(fields_frame, text="Usuario:").pack(anchor="w")
        self.usuario_entry = ttk.Entry(fields_frame, width=50)
        self.usuario_entry.insert(0, usuario)
        self.usuario_entry.configure(state='readonly')
        self.usuario_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(fields_frame, text="Nueva clave:").pack(anchor="w")
        self.nueva_clave = ttk.Entry(fields_frame, show="*", width=50)
        self.nueva_clave.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(fields_frame, text="Confirmar clave:").pack(anchor="w")
        self.confirmar_clave = ttk.Entry(fields_frame, show="*", width=50)
        self.confirmar_clave.pack(fill=tk.X, pady=(0, 10))

        # Campos para pregunta de seguridad
        ttk.Label(fields_frame, text="Pregunta de seguridad:").pack(anchor="w")
        self.preguntas = [
            "¿Cuál es el nombre de tu primera mascota?",
            "¿En qué ciudad naciste?",
            "¿Cuál es el nombre de tu mejor amigo de la infancia?",
            "¿Cuál es tu comida favorita?",
            "¿Cuál es el segundo nombre de tu madre?"
        ]
        self.pregunta_var = tk.StringVar()
        self.pregunta_combo = Combobox(fields_frame, 
                                     textvariable=self.pregunta_var,
                                     values=self.preguntas,
                                     width=47,
                                     state="readonly")
        self.pregunta_combo.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(fields_frame, text="Respuesta:").pack(anchor="w")
        self.respuesta_entry = ttk.Entry(fields_frame, width=50)
        self.respuesta_entry.pack(fill=tk.X, pady=(0, 10))

        # Frame para requisitos
        req_frame = ttk.LabelFrame(main_frame, text="Requisitos de la contraseña", padding=10)
        req_frame.pack(fill=tk.X, pady=15)

        requisitos = [
            "Mínimo 8 caracteres",
            "Al menos una letra mayúscula",
            "Al menos una letra minúscula",
            "Al menos un número",
            "Al menos un carácter especial (!@#$%^&*)"
        ]

        for req in requisitos:
            ttk.Label(req_frame, text="• " + req).pack(anchor="w", pady=2)
            
        self.error_label = ttk.Label(main_frame, text="", style="Error.TLabel")
        self.error_label.pack(pady=10)

        ttk.Button(main_frame, text="Guardar", 
                  command=self.guardar_cambios).pack(pady=10)

        self.protocol("WM_DELETE_WINDOW", lambda: None)

    def guardar_cambios(self):
        nueva = self.nueva_clave.get()
        confirmar = self.confirmar_clave.get()
        pregunta = self.pregunta_var.get()
        respuesta = self.respuesta_entry.get()
        
        if not all([nueva, confirmar, pregunta, respuesta]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
            
        if nueva != confirmar:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
            
        errores = self.validar_contraseña(nueva)
        if errores:
            messagebox.showerror("Error", "\n".join(errores))
            return
            
        try:
            # Encriptar contraseña
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(nueva.encode('utf-8'), salt)
            
            # Encriptar respuesta de seguridad
            salt_resp = bcrypt.gensalt()
            hashed_respuesta = bcrypt.hashpw(respuesta.encode('utf-8'), salt_resp)
            
            query = """
            UPDATE usuarios 
            SET contraseña = %s, 
                primer_ingreso = FALSE,
                pregunta_seguridad = %s,
                respuesta_seguridad = %s
            WHERE usuario = %s
            """
            self.db_manager.ejecutar_query(
                query, 
                (hashed_password.decode('utf-8'), 
                pregunta, 
                hashed_respuesta.decode('utf-8'), 
                self.usuario), 
                commit=True
            )
            messagebox.showinfo("Éxito", "Configuración guardada exitosamente")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar cambios: {str(e)}")

    def validar_contraseña(self, contraseña):
        errores = []
        if len(contraseña) < 8:
            errores.append("La contraseña debe tener al menos 8 caracteres")
        if not any(c.isupper() for c in contraseña):
            errores.append("Debe incluir al menos una letra mayúscula")
        if not any(c.islower() for c in contraseña):
            errores.append("Debe incluir al menos una letra minúscula")
        if not any(c.isdigit() for c in contraseña):
            errores.append("Debe incluir al menos un número")
        if not any(c in "!@#$%^&*" for c in contraseña):
            errores.append("Debe incluir al menos un carácter especial (!@#$%^&*)")
        return errores

class RecuperarClaveForm(tk.Toplevel):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.title("Recuperar Contraseña")
        self.geometry("500x450")  # Reducido ya que mostraremos menos contenido a la vez
        self.configure(bg="#f0f0f0")
        
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame para búsqueda de usuario
        self.search_frame = ttk.LabelFrame(main_frame, text="Buscar Usuario", padding="10")
        self.search_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(self.search_frame, text="Usuario:").pack(anchor="w")
        self.usuario_entry = ttk.Entry(self.search_frame, width=50)
        self.usuario_entry.pack(fill=tk.X, pady=5)
        
        self.buscar_btn = ttk.Button(
            self.search_frame, 
            text="Buscar",
            style="Accent.TButton",
            command=self.buscar_usuario
        )
        self.buscar_btn.pack(pady=5)
        
        # Frame para pregunta de seguridad (inicialmente oculto)
        self.security_frame = ttk.LabelFrame(main_frame, text="Pregunta de Seguridad", padding="10")
        
        self.pregunta_label = ttk.Label(
            self.security_frame, 
            text="",
            wraplength=450,
            style="Question.TLabel"
        )
        self.pregunta_label.pack(pady=5)
        
        ttk.Label(self.security_frame, text="Respuesta:").pack(anchor="w")
        self.respuesta_entry = ttk.Entry(self.security_frame, show="*", width=50)
        self.respuesta_entry.pack(fill=tk.X, pady=5)
        
        self.verificar_btn = ttk.Button(
            self.security_frame,
            text="Verificar Respuesta",
            command=self.verificar_respuesta
        )
        self.verificar_btn.pack(pady=5)
        
        # Frame para nueva contraseña (inicialmente oculto)
        self.password_frame = ttk.LabelFrame(main_frame, text="Nueva Contraseña", padding="10")
        
        # Frame para requisitos
        self.req_frame = ttk.LabelFrame(self.password_frame, text="Requisitos de la contraseña", padding="10")
        self.req_frame.pack(fill=tk.X, pady=(0, 10))
        
        requisitos = [
            "Mínimo 8 caracteres",
            "Al menos una letra mayúscula",
            "Al menos una letra minúscula",
            "Al menos un número",
            "Al menos un carácter especial (!@#$%^&*)"
        ]
        
        for req in requisitos:
            ttk.Label(self.req_frame, text="• " + req).pack(anchor="w", pady=2)
        
        ttk.Label(self.password_frame, text="Nueva contraseña:").pack(anchor="w")
        self.nueva_clave_entry = ttk.Entry(self.password_frame, show="*", width=50)
        self.nueva_clave_entry.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.password_frame, text="Confirmar contraseña:").pack(anchor="w")
        self.confirmar_clave_entry = ttk.Entry(self.password_frame, show="*", width=50)
        self.confirmar_clave_entry.pack(fill=tk.X, pady=5)
        
        self.recuperar_btn = ttk.Button(
            self.password_frame,
            text="Actualizar Contraseña",
            style="Accent.TButton",
            command=self.recuperar_clave
        )
        self.recuperar_btn.pack(pady=10)
        
        # Configurar estilos
        self.setup_styles()
        
    def setup_styles(self):
        style = ttk.Style()
        style.configure(
            "Question.TLabel",
            font=("Arial", 10, "bold")
        )
    
    def validar_contraseña(self, contraseña):
        errores = []
        
        if len(contraseña) < 8:
            errores.append("La contraseña debe tener al menos 8 caracteres")
            
        if not any(c.isupper() for c in contraseña):
            errores.append("La contraseña debe contener al menos una mayúscula")
            
        if not any(c.islower() for c in contraseña):
            errores.append("La contraseña debe contener al menos una minúscula")
            
        if not any(c.isdigit() for c in contraseña):
            errores.append("La contraseña debe contener al menos un número")
            
        if not any(c in "!@#$%^&*" for c in contraseña):
            errores.append("La contraseña debe contener al menos un carácter especial (!@#$%^&*)")
            
        return errores
        
    def buscar_usuario(self):
        usuario = self.usuario_entry.get()
        if not usuario:
            messagebox.showerror("Error", "Por favor ingrese un usuario")
            return
            
        query = """
        SELECT pregunta_seguridad
        FROM usuarios
        WHERE usuario = %s
        """
        result = self.db_manager.ejecutar_query(query, (usuario,), fetchone=True)
        
        if result and result[0]:
            self.pregunta_label.config(text=result[0])
            self.usuario_entry.config(state='readonly')
            self.buscar_btn.config(state='disabled')
            
            # Mostrar frame de seguridad y ocultar frame de búsqueda
            self.search_frame.pack_forget()
            self.security_frame.pack(fill=tk.X, pady=10)
        else:
            messagebox.showerror("Error", "Usuario no encontrado")
            
    def verificar_respuesta(self):
        usuario = self.usuario_entry.get()
        respuesta = self.respuesta_entry.get()
        
        if not respuesta:
            messagebox.showerror("Error", "Por favor ingrese una respuesta")
            return
        
        query = """
        SELECT respuesta_seguridad
        FROM usuarios
        WHERE usuario = %s
        """
        result = self.db_manager.ejecutar_query(query, (usuario,), fetchone=True)
        
        stored_hash = result[0].encode('utf-8')
        if bcrypt.checkpw(respuesta.encode('utf-8'), stored_hash):
            # Ocultar frame de seguridad y mostrar frame de contraseña
            self.security_frame.pack_forget()
            self.password_frame.pack(fill=tk.X, pady=10)
        else:
            messagebox.showerror("Error", "Respuesta incorrecta")
            
    def recuperar_clave(self):
        """Actualizar contraseña y desbloquear usuario si es necesario"""
        usuario = self.usuario_entry.get()
        nueva_clave = self.nueva_clave_entry.get()
        confirmar_clave = self.confirmar_clave_entry.get()
        
        if nueva_clave != confirmar_clave:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        
        # Validar contraseña
        errores = self.validar_contraseña(nueva_clave)
        if errores:
            messagebox.showerror("Error", "\n".join(errores))
            return
        
        try:
            # Verificar estado actual del usuario
            query_estado = "SELECT estado FROM usuarios WHERE usuario = %s"
            estado_actual = self.db_manager.ejecutar_query(
                query_estado, 
                (usuario,), 
                fetchone=True
            )
            
            if not estado_actual:
                messagebox.showerror("Error", "Usuario no encontrado")
                return
                
            # Actualizar contraseña y resetear intentos
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(nueva_clave.encode('utf-8'), salt)
            
            update_query = """
            UPDATE usuarios
            SET contraseña = %s,
                intentos_fallidos = 0,
                estado = 'activo'
            WHERE usuario = %s
            """
            
            self.db_manager.ejecutar_query(
                update_query,
                (hashed_password.decode('utf-8'), usuario),
                commit=True
            )
            
            # Mensaje personalizado según el estado anterior
            if estado_actual[0] == 'bloqueado':
                mensaje = "Contraseña actualizada exitosamente.\nSu cuenta ha sido desbloqueada."
            else:
                mensaje = "Contraseña actualizada exitosamente."
                
            messagebox.showinfo("Éxito", mensaje)
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

class LoginForm(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.is_logged_in = False
        self.username = ""
        
        self.db_manager = DatabaseManager(**DB_CONFIG)
        
        # Configuración de la ventana
        self.title("NomiInversiones - R.H.G Inversiones, C.A.")
        self.geometry("745x424")
        self.configure(bg="#ffffff")
        self.resizable(False, False)
        
        # Crear estilos personalizados
        self.create_styles()
        
        # Frame izquierdo para el formulario
        left_frame = ttk.Frame(self, style="White.TFrame")
        left_frame.place(x=0, y=0, width=320, height=404)
        
        # Título
        tk.Label(left_frame, 
                text="NomiInversiones",
                bg="#ffffff",
                font=("Arial", 16, "bold")).place(x=40, y=30)
        
        # Subtítulo
        tk.Label(left_frame,
                text="R.H.G Inversiones, C.A.",
                bg="#ffffff",
                fg="#666666",
                font=("Arial", 10)).place(x=40, y=60)
        
        # Campo de usuario
        tk.Label(left_frame, 
                text="Usuario",
                bg="#ffffff",
                font=("Arial", 10)).place(x=20, y=120)
        
        self.user_entry = ttk.Entry(left_frame, 
                                  font=("Arial", 10),
                                  width=35)
        self.user_entry.place(x=20, y=145)
        self.user_entry.insert(0, "admin")
        
        # Campo de contraseña
        tk.Label(left_frame,
                text="Contraseña",
                bg="#ffffff",
                font=("Arial", 10)).place(x=20, y=180)
        
        self.password_entry = ttk.Entry(left_frame,
                                      font=("Arial", 10),
                                      width=35,
                                      show="*")
        self.password_entry.place(x=20, y=205)
        self.password_entry.insert(0, "admin1")
        
        # Botones
        style = ttk.Style()
        style.configure("Login.TButton",
                      font=("Arial", 10),
                      padding=10)
        
        login_button = tk.Button(
            left_frame,
            text="Iniciar Sesión",
            font=("Arial", 10, "bold"),
            fg="#ffffff",  # Texto blanco
            bg="#2596be", # Azul corporativo
            activebackground="#1e7aa3",  # Azul más oscuro para hover
            relief="flat",
            cursor="hand2",
            command=self.login
        )
        login_button.place(x=20, y=320, width=280, height=35)

        login_button.bind("<Enter>", lambda e: e.widget.config(bg="#1e7aa3"))
        login_button.bind("<Leave>", lambda e: e.widget.config(bg="#2596be"))

        exit_button = tk.Button(
            left_frame,
            text="Salir",
            font=("Arial", 10),
            fg="#ffffff",  # Texto blanco
            bg="#dc3545",  # Rojo para el botón de salir
            activebackground="#c82333",  # Rojo más oscuro para hover
            relief="flat",
            cursor="hand2",
            command=self.exit
        )
        exit_button.place(x=20, y=365, width=280, height=35)

        forgot_button = tk.Button(
            left_frame,
            text="¿Olvidaste tu contraseña?",
            font=("Arial", 10),
            fg="#2596be",
            bg="#ffffff",
            bd=0,
            cursor="hand2",
            command=self.recuperar_clave
        )
        forgot_button.place(x=20, y=240)
        
        # Frame derecho para la imagen
        right_frame = ttk.Frame(self)
        right_frame.place(x=320, y=0, width=425, height=404)
        
        try:
            # Cargar y mostrar el logo
            img = Image.open("./imagenes/Logo RHG.jpg")
            img_resized = img.resize((421, 401), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(img_resized)
            logo_label = tk.Label(right_frame,
                                image=self.logo,
                                bg="#ffffff")
            logo_label.place(x=0, y=0)
        except Exception as e:
            print(f"Error al cargar la imagen: {e}")
            
        # Label para mensajes de error
        self.error_label = tk.Label(left_frame,
                                  text="",
                                  bg="#ffffff",
                                  fg="#ff0000",
                                  font=("Arial", 9),
                                  wraplength=280,
                                  justify='left',
                                  pady=10)
        self.error_label.place(x=20, y=270, width=280, height=40)
        
        # Centrar la ventana
        self.center_window()
        
    def create_styles(self):
        style = ttk.Style()
        style.configure("White.TFrame", background="#ffffff")
        style.configure("TEntry", padding=5)
        style.configure("TButton",
                      padding=10,
                      font=("Arial", 10))
        
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')


    def recuperar_clave(self):
        RecuperarClaveForm(self, self.db_manager)

    def login(self):
        username = self.user_entry.get()
        password = self.password_entry.get().encode('utf-8')
        
        try:
            if self.db_manager.verify_credentials(username, password):
                # Verificar primer ingreso
                primer_ingreso, permisos = self.db_manager.verificar_primer_ingreso(username)
                
                if primer_ingreso:
                    cambio_form = CambioClaveForm(self, self.db_manager, username)
                    self.wait_window(cambio_form)
                
                self.username = username
                self.permisos = permisos
                self.is_logged_in = True
                self.quit()
                self.open_main_app()
            else:
                self.error_label.config(text="Usuario o contraseña incorrectos")
        except Exception as e:
            self.error_label.config(text=str(e))

    def exit(self):
        self.is_logged_in = False
        self.destroy()

    def open_main_app(self):
        self.quit()
        self.destroy()
        main_app = MainApp(username = self.username)
        main_app.mainloop()

if __name__ == "__main__":
    app = LoginForm()
    app.mainloop()