import tkinter as tk
import bcrypt
import random
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from util.db_manager import DatabaseManager
from util.config import DB_CONFIG
from formularios.form_master import MainApp
from tkinter.ttk import Combobox
from ttkthemes import ThemedStyle

class CambioClaveForm(tk.Toplevel):
    def __init__(self, parent, db_manager, usuario):
        super().__init__(parent)
        self.db_manager = db_manager
        self.usuario = usuario
        
        self.title("Configuración Inicial")
        self.geometry("600x650")
        
        # Frame principal con scroll
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Canvas para scroll
        canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        
        # Frame scrollable
        self.scrollable_frame = ttk.Frame(canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=580)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Configurar grid
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        canvas.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Contenido
        main_frame = ttk.Frame(self.scrollable_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        

        # Título mejorado
        ttk.Label(main_frame, 
                text="Cambio de clave y preguntas de seguridad",
                font=('Arial', 16, 'bold'),
                foreground="#2596be").pack(pady=(0, 20))

        # Frame de contraseña mejorado
        pwd_frame = ttk.LabelFrame(main_frame, text="Cambio de Contraseña", padding="15")
        pwd_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Agregar los requisitos de contraseña
        requisitos_frame = ttk.Frame(pwd_frame)
        requisitos_frame.pack(fill=tk.X, pady=5)
        
        requisitos = [
            "• Al menos 8 caracteres",
            "• Una letra mayúscula",
            "• Una letra minúscula",
            "• Al menos un número",
            "• Un carácter especial (!@#$%^&*)"
        ]
        
        for req in requisitos:
            ttk.Label(requisitos_frame, 
                    text=req,
                    font=("Arial", 9),
                    foreground="#666666").pack(anchor="w")

        ttk.Label(pwd_frame, text="Nueva clave:", 
                font=("Arial", 10)).pack(anchor="w", pady=(10,0))
        self.nueva_clave = ttk.Entry(pwd_frame, show="*", width=50)
        self.nueva_clave.pack(fill=tk.X, pady=5)
        
        ttk.Label(pwd_frame, text="Confirmar clave:",
                font=("Arial", 10)).pack(anchor="w", pady=(10,0))
        self.confirmar_clave = ttk.Entry(pwd_frame, show="*", width=50)
        self.confirmar_clave.pack(fill=tk.X, pady=5)

        # Frame para preguntas predefinidas
        predef_frame = ttk.LabelFrame(main_frame, text="Preguntas Predefinidas", padding="15")
        predef_frame.pack(fill=tk.X, padx=20, pady=10)

        self.preguntas_pred = self.obtener_preguntas_predefinidas()
        self.preguntas_vars = []
        self.respuestas_entries = []

        for i in range(2):
            subframe = ttk.Frame(predef_frame)
            subframe.pack(fill=tk.X, pady=5)
            
            ttk.Label(subframe, 
                    text=f"Pregunta {i+1}:", 
                    font=("Arial", 10, "bold"),
                    foreground="#2596be",
                    width=15).pack(side=tk.LEFT)
            
            pregunta_var = tk.StringVar()
            self.preguntas_vars.append(pregunta_var)
            
            combo = ttk.Combobox(subframe, 
                            textvariable=pregunta_var,
                            values=[p[1] for p in self.preguntas_pred],
                            width=45,
                            state="readonly")
            combo.pack(side=tk.LEFT, padx=(5,0))
            
            resp_frame = ttk.Frame(predef_frame)
            resp_frame.pack(fill=tk.X, pady=(0,10))
            
            ttk.Label(resp_frame, 
                    text="Respuesta:", 
                    font=("Arial", 9),
                    foreground="#666666",
                    width=15).pack(side=tk.LEFT)
            resp_entry = ttk.Entry(resp_frame, show="*", width=47)
            resp_entry.pack(side=tk.LEFT, padx=(5,0))
            self.respuestas_entries.append(resp_entry)

        # Frame para preguntas personalizadas
        pers_frame = ttk.LabelFrame(main_frame, text="Preguntas Personalizadas", padding="15")
        pers_frame.pack(fill=tk.X, padx=20, pady=10)

        self.preguntas_custom = []
        self.respuestas_custom = []

        for i in range(2):
            q_frame = ttk.Frame(pers_frame) 
            q_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(q_frame,
                        text=f"Pregunta {i+1}:",
                        font=("Arial", 10, "bold"),
                        foreground="#2596be",
                        width=15).pack(side=tk.LEFT)
            
            preg_entry = ttk.Entry(q_frame, width=47)
            preg_entry.pack(side=tk.LEFT, padx=(5,0))
            self.preguntas_custom.append(preg_entry)
            
            r_frame = ttk.Frame(pers_frame)
            r_frame.pack(fill=tk.X, pady=(0,10))
            
            ttk.Label(r_frame,
                        text="Respuesta:",
                        font=("Arial", 9), 
                        foreground="#666666",
                        width=15).pack(side=tk.LEFT)
            
            resp_entry = ttk.Entry(r_frame, show="*", width=47)
            resp_entry.pack(side=tk.LEFT, padx=(5,0))
            self.respuestas_custom.append(resp_entry)

        # Botón guardar
        tk.Button(main_frame,
                text="Guardar",
                font=("Arial", 10, "bold"),
                fg="#ffffff",
                bg="#2596be",
                activebackground="#1e7aa3",
                relief="flat",
                cursor="hand2",
                command=self.guardar_cambios).pack(pady=20)

        # Binding para scroll con rueda del mouse
        self.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        self.protocol("WM_DELETE_WINDOW", lambda: None)

    def obtener_preguntas_predefinidas(self):
        query = "SELECT id, pregunta FROM preguntas_predefinidas"
        return self.db_manager.ejecutar_query(query)

    def guardar_cambios(self):
        if not self.validar_datos():
            return

        try:
            # Encriptar contraseña
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(self.nueva_clave.get().encode('utf-8'), salt)
            
            # Actualizar contraseña
            query = """
            UPDATE usuarios 
            SET contraseña = %s, 
                primer_ingreso = FALSE
            WHERE usuario = %s
            """
            self.db_manager.ejecutar_query(query, 
                (hashed_password.decode('utf-8'), self.usuario), 
                commit=True)

            # Guardar preguntas predefinidas
            for i in range(2):
                pregunta_id = next(p[0] for p in self.preguntas_pred 
                                 if p[1] == self.preguntas_vars[i].get())
                respuesta = self.respuestas_entries[i].get()
                
                salt_resp = bcrypt.gensalt()
                hashed_resp = bcrypt.hashpw(respuesta.encode('utf-8'), salt_resp)
                
                query = """
                INSERT INTO preguntas_seguridad_usuario 
                (id_usuario, id_pregunta_predefinida, respuesta, tipo)
                VALUES (
                    (SELECT id_usuario FROM usuarios WHERE usuario = %s),
                    %s, %s, 'predefinida'
                )
                """
                self.db_manager.ejecutar_query(query, 
                    (self.usuario, pregunta_id, hashed_resp.decode('utf-8')),
                    commit=True)

            # Guardar preguntas personalizadas
            for i in range(2):
                pregunta = self.preguntas_custom[i].get()
                respuesta = self.respuestas_custom[i].get()
                
                salt_resp = bcrypt.gensalt()
                hashed_resp = bcrypt.hashpw(respuesta.encode('utf-8'), salt_resp)
                
                query = """
                INSERT INTO preguntas_seguridad_usuario 
                (id_usuario, pregunta_personalizada, respuesta, tipo)
                VALUES (
                    (SELECT id_usuario FROM usuarios WHERE usuario = %s),
                    %s, %s, 'personalizada'
                )
                """
                self.db_manager.ejecutar_query(query,
                    (self.usuario, pregunta, hashed_resp.decode('utf-8')),
                    commit=True)

            messagebox.showinfo("Éxito", "Configuración guardada exitosamente")
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar cambios: {str(e)}")

    def validar_datos(self):
        nueva = self.nueva_clave.get()
        confirmar = self.confirmar_clave.get()
        
        if not all([nueva, confirmar]):
            messagebox.showerror("Error", "La contraseña es obligatoria")
            return False
            
        if nueva != confirmar:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return False
            
        errores = self.validar_contraseña(nueva)
        if errores:
            messagebox.showerror("Error", "\n".join(errores))
            return False

        # Validar preguntas predefinidas
        if not all(v.get() for v in self.preguntas_vars):
            messagebox.showerror("Error", "Debe seleccionar todas las preguntas predefinidas")
            return False

        if not all(e.get() for e in self.respuestas_entries):
            messagebox.showerror("Error", "Debe responder todas las preguntas predefinidas")
            return False

        # Validar preguntas personalizadas
        if not all(e.get() for e in self.preguntas_custom):
            messagebox.showerror("Error", "Debe ingresar todas las preguntas personalizadas")
            return False

        if not all(e.get() for e in self.respuestas_custom):
            messagebox.showerror("Error", "Debe responder todas las preguntas personalizadas")
            return False

        return True

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
        self.geometry("500x400")
        self.configure(bg="#ffffff")
        
        # Frame principal con padding
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True)

        self.respuestas_entries = []
        self.preguntas_respuestas = []

        # Título y subtítulo
        self.title_frame = ttk.Frame(main_container)
        self.title_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Label(
            self.title_frame,
            text="¿Olvidaste tu contraseña?",
            font=("Arial", 16, "bold"),
            foreground="#2596be"
        ).pack()

        ttk.Label(
            self.title_frame,
            text="Ingresa tu usuario para comenzar el proceso de recuperación",
            font=("Arial", 10),
            foreground="#666666",
            wraplength=400
        ).pack(pady=(5,0))
        
        # Frame de búsqueda
        self.search_frame = ttk.LabelFrame(main_container, text="Buscar Usuario", padding="15")
        self.search_frame.pack(fill=tk.X, pady=10, padx=20)
        
        ttk.Label(self.search_frame, text="Usuario (Cédula):", 
                 font=("Arial", 10)).pack(anchor="w")
        self.usuario_entry = ttk.Entry(self.search_frame, width=50)
        self.usuario_entry.pack(fill=tk.X, pady=5)
        
        self.buscar_btn = tk.Button(
            self.search_frame,
            text="Buscar",
            font=("Arial", 10),
            fg="#ffffff",
            bg="#2596be",
            activebackground="#1e7aa3",
            relief="flat",
            cursor="hand2",
            command=self.buscar_usuario
        )
        self.buscar_btn.pack(pady=10)
        
        # Mantener referencias a frames originales
        self.security_frame = ttk.LabelFrame(main_container, text="Preguntas de Seguridad", padding="10")
        self.password_frame = ttk.LabelFrame(main_container, text="Nueva Contraseña", padding="10")
        
        # Variables para las preguntas y respuestas
        self.preguntas_respuestas = []
        self.usuario_id = None
        
        # # Binding para scroll con rueda del mouse
        # self.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def buscar_usuario(self):
        usuario = self.usuario_entry.get()
        if not usuario:
            messagebox.showerror("Error", "Por favor ingrese un usuario")
            return
            
        query = """
        SELECT u.id_usuario, u.estado
        FROM usuarios u
        WHERE u.usuario = %s
        """
        result = self.db_manager.ejecutar_query(query, (usuario,), fetchone=True)
        
        if not result:
            messagebox.showerror("Error", "Usuario no encontrado")
            return
            
        self.usuario_id = result[0]
        estado = result[1]
        
        if estado == 'bloqueado':
            messagebox.showerror("Error", "Usuario bloqueado. Contacte al administrador.")
            return
            
        # Obtener preguntas de seguridad aleatorias
        self.obtener_preguntas_aleatorias()
        
        if not self.preguntas_respuestas:
            messagebox.showerror("Error", "No se pudieron obtener las preguntas de seguridad")
            return
            
        # Mostrar frame de preguntas
        self.mostrar_preguntas_seguridad()

    def obtener_preguntas_aleatorias(self):
        """Obtener 2-3 preguntas aleatorias del usuario"""
        query = """
        SELECT ps.id, 
               COALESCE(pp.pregunta, ps.pregunta_personalizada) as pregunta,
               ps.respuesta,
               ps.tipo
        FROM preguntas_seguridad_usuario ps
        LEFT JOIN preguntas_predefinidas pp ON ps.id_pregunta_predefinida = pp.id
        WHERE ps.id_usuario = %s
        """
        preguntas = self.db_manager.ejecutar_query(query, (self.usuario_id,))
        
        if preguntas:
            # Seleccionar 2-3 preguntas aleatoriamente
            num_preguntas =  3
            self.preguntas_respuestas = random.sample(preguntas, num_preguntas)

    def mostrar_preguntas_seguridad(self):

        self.geometry("500x650")

        for widget in self.title_frame.winfo_children():
            widget.pack_forget()
        self.search_frame.pack_forget()
        
        ttk.Label(
            self.title_frame, 
            text="Preguntas de Seguridad",
            font=("Arial", 16, "bold"),
            foreground="#2596be"
        ).pack()
        
        ttk.Label(
            self.title_frame,
            text="Por favor responde las siguientes preguntas para verificar tu identidad",
            font=("Arial", 10),
            foreground="#666666",
            wraplength=400
        ).pack(pady=(5,15))
        
        # Frame de preguntas con estilo mejorado
        self.security_frame.pack(fill=tk.X, pady=10, padx=30)
        
        for i, (id_pregunta, pregunta, respuesta_hash, tipo) in enumerate(self.preguntas_respuestas):
            pregunta_frame = ttk.Frame(self.security_frame)
            pregunta_frame.pack(fill=tk.X, pady=15)
            
            ttk.Label(
                pregunta_frame,
                text=f"Pregunta {i+1}:",
                font=("Arial", 10, "bold"),
                foreground="#2596be"
            ).pack(anchor="w")
            
            ttk.Label(
                pregunta_frame,
                text=pregunta,
                font=("Arial", 10),
                wraplength=400
            ).pack(anchor="w", pady=(5,0))
            
            ttk.Label(
                pregunta_frame, 
                text="Respuesta:",
                font=("Arial", 9),
                foreground="#666666"
            ).pack(anchor="w", pady=(10,0))
            
            entry = ttk.Entry(pregunta_frame, show="*", width=50)
            entry.pack(pady=(5,0), fill=tk.X)
            self.respuestas_entries.append((entry, respuesta_hash))
        
        # Botón verificar
        btn_verificar = tk.Button(
            self.security_frame,
            text="Verificar Respuestas",
            font=("Arial", 10, "bold"),
            fg="#ffffff",
            bg="#2596be",
            activebackground="#1e7aa3",
            relief="flat",
            cursor="hand2",
            command=self.verificar_respuestas
        )
        btn_verificar.pack(pady=20)

    def verificar_respuestas(self):
        respuestas_correctas = 0
        
        for entry, hash_stored in self.respuestas_entries:
            respuesta = entry.get().strip()
            if not respuesta:
                messagebox.showerror("Error", "Por favor complete todas las respuestas")
                return
                
            if bcrypt.checkpw(respuesta.encode('utf-8'), hash_stored.encode('utf-8')):
                respuestas_correctas += 1
        
        # Verificar umbral de respuestas correctas (2/3 o 2/2)
        umbral = len(self.respuestas_entries) - 1 if len(self.respuestas_entries) > 2 else len(self.respuestas_entries)
        
        if respuestas_correctas >= umbral:
            self.mostrar_cambio_password()
        else:
            messagebox.showerror("Error", "Respuestas incorrectas")

    def mostrar_cambio_password(self):
        self.geometry("500x650")
        self.security_frame.pack_forget()
        for widget in self.title_frame.winfo_children():
            widget.pack_forget()
        
        ttk.Label(
            self.title_frame, 
            text="Configuración de contraseña",
            font=("Arial", 16, "bold"),
            foreground="#2596be"
        ).pack()
        
        ttk.Label(
            self.title_frame,
            text="Por favor establece una nueva contraseña segura",
            font=("Arial", 10),
            foreground="#666666",
            wraplength=400
        ).pack(pady=(5,15))

        # Frame para requisitos con estilo mejorado
        requisitos_frame = ttk.Frame(self.password_frame)
        requisitos_frame.pack(fill=tk.X, pady=10, padx=30)

        ttk.Label(
            requisitos_frame,
            text="Requisitos de seguridad:",
            font=("Arial", 10, "bold"),
            foreground="#2596be"
        ).pack(anchor="w", pady=(0,5))

        requisitos = [
            "Al menos 8 caracteres",
            "Una letra mayúscula",
            "Una letra minúscula", 
            "Al menos un número",
            "Un carácter especial (!@#$%^&*)"
        ]

        for req in requisitos:
            req_frame = ttk.Frame(requisitos_frame)
            req_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(
                req_frame,
                text="•",
                font=("Arial", 10),
                foreground="#666666"
            ).pack(side=tk.LEFT, padx=(0,5))
            
            ttk.Label(
                req_frame,
                text=req,
                font=("Arial", 10),
                foreground="#666666"
            ).pack(side=tk.LEFT)

        # Frame para nueva contraseña
        password_frame = ttk.Frame(self.password_frame)
        password_frame.pack(fill=tk.X, pady=20, padx=30)

        ttk.Label(
            password_frame,
            text="Nueva contraseña:",
            font=("Arial", 10),
            foreground="#666666"
        ).pack(anchor="w")
        
        self.nueva_clave_entry = ttk.Entry(password_frame, show="*", width=50)
        self.nueva_clave_entry.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            password_frame,
            text="Confirmar contraseña:", 
            font=("Arial", 10),
            foreground="#666666"
        ).pack(anchor="w", pady=(10,0))
        
        self.confirmar_clave_entry = ttk.Entry(password_frame, show="*", width=50)
        self.confirmar_clave_entry.pack(fill=tk.X, pady=5)

        # Botón actualizar con estilo consistente
        btn_actualizar = tk.Button(
            self.password_frame,
            text="Actualizar Contraseña",
            font=("Arial", 10, "bold"),
            fg="#ffffff",
            bg="#2596be",
            activebackground="#1e7aa3",
            relief="flat",
            cursor="hand2",
            command=self.actualizar_password
        )
        btn_actualizar.pack(pady=20)

        # Mostrar el frame principal
        self.password_frame.pack(fill=tk.X, pady=10, padx=30)
            
    def actualizar_password(self):
        nueva_clave = self.nueva_clave_entry.get()
        confirmar_clave = self.confirmar_clave_entry.get()
        
        if nueva_clave != confirmar_clave:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
            
        errores = self.validar_contraseña(nueva_clave)
        if errores:
            messagebox.showerror("Error", "\n".join(errores))
            return
            
        try:
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(nueva_clave.encode('utf-8'), salt)
            
            query = """
            UPDATE usuarios
            SET contraseña = %s,
                intentos_fallidos = 0,
                estado = 'activo'
            WHERE id_usuario = %s
            """
            
            self.db_manager.ejecutar_query(query, 
                (hashed_password.decode('utf-8'), self.usuario_id),
                commit=True)
                
            messagebox.showinfo("Éxito", "Contraseña actualizada exitosamente")
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar contraseña: {str(e)}")

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
        ttk.Label(left_frame,
                text="Usuario (Cédula):",
                font=("Arial", 10),
                background="#ffffff").place(x=20, y=125)
        self.user_entry = ttk.Entry(left_frame, 
                                font=("Arial", 10),
                                width=35)
        self.user_entry.place(x=20, y=145)
        self.user_entry.insert(0, "27289467")
        # Vincular Enter para pasar a contraseña
        self.user_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.user_entry.focus()
        
        # Campo de contraseña
        ttk.Label(left_frame,
                text="Contraseña:",
                font=("Arial", 10),
                background="#ffffff").place(x=20, y=185)
        
        self.password_entry = ttk.Entry(left_frame,
                                    font=("Arial", 10),
                                    width=35,
                                    show="*")
        self.password_entry.place(x=20, y=205)
        self.password_entry.insert(0, "Poko789*")
        # Vincular Enter para hacer login
        self.password_entry.bind('<Return>', lambda e: self.login())
        
        # Botones
        style = ttk.Style()
        style.configure("Login.TButton",
                      font=("Arial", 10),
                      padding=10)
        
        login_button = tk.Button(
            left_frame,
            text="  Iniciar Sesión",  # Espacios para simular padding con el ícono
            font=("Arial", 10, "bold"),
            fg="#ffffff",
            bg="#0D6EFD", 
            activebackground="#0B5ED7",
            relief="flat",
            cursor="hand2",
            command=self.login
        )
        login_button.place(x=20, y=320, width=280, height=35)

        # Eventos Hover
        login_button.bind("<Enter>", lambda e: e.widget.config(bg="#0B5ED7"))
        login_button.bind("<Leave>", lambda e: e.widget.config(bg="#0D6EFD"))

        exit_button = tk.Button(
            left_frame,
            text="  Salir",
            font=("Arial", 10, "bold"),
            fg="#ffffff",
            bg="#9A9EA1",
            activebackground="#6C757D",
            activeforeground="#9A9EA1",
            relief="flat",
            borderwidth=1,
            cursor="hand2",
            command=self.exit
        )
        exit_button.place(x=20, y=365, width=280, height=35)

        # Eventos hover para el botón salir
        exit_button.bind("<Enter>", lambda e: (
            e.widget.config(bg="#6C757D", fg="#ffffff")))
        exit_button.bind("<Leave>", lambda e: (
            e.widget.config(bg="#9A9EA1", fg="#ffffff")))

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

                # Obtener el rol con consulta en la base de datos
                rol_query = "SELECT rol FROM usuarios WHERE usuario = %s"
                rol = self.db_manager.ejecutar_query(rol_query, (username,), fetchone=True)[0]

                # Registro Auditoria
                self.db_manager.registrar_auditoria(
                    usuario=username,
                    rol=rol,
                    accion='Inicio Sesión',
                    tabla='usuarios',
                    detalle=f"Inicio de sesión exitoso desde la aplicación"
                )
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