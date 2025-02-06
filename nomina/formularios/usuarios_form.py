import tkinter as tk
from tkinter import ttk, messagebox
import bcrypt
from datetime import datetime
from util.ayuda import Ayuda

class GestionPermisosForm(tk.Toplevel):
    """Formulario para gestionar los permisos de un usuario"""
    def __init__(self, parent, db_manager, id_usuario):
        super().__init__(parent)
        self.parent = parent
        self.db_manager = db_manager
        self.id_usuario = id_usuario
        
        # Configuración básica
        self.title("Gestión de Permisos")
        self.geometry("600x500")
        
        # Frame principal con scroll
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas y scrollbar para permitir scroll
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=550)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar elementos del scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Obtener información del usuario
        usuario_info = self.obtener_info_usuario()
        if usuario_info:
            # Mostrar información del usuario
            info_frame = ttk.LabelFrame(scroll_frame, text="Información del Usuario", padding="10")
            info_frame.pack(fill=tk.X, pady=(0,10))
            
            ttk.Label(info_frame, text=f"Usuario: {usuario_info['usuario']}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Nombre: {usuario_info['nombre']}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Rol: {usuario_info['rol']}").pack(anchor='w')
        
        # Frame para permisos
        permisos_frame = ttk.LabelFrame(scroll_frame, text="Permisos del Sistema", padding="10")
        permisos_frame.pack(fill=tk.X)
        
        # Diccionario para almacenar las variables de los submódulos y sus alcances
        self.submodulos_vars = {}
        
        # Definir estructura de módulos y submódulos
        modulos = {
            "Empleados": [
                ("Gestionar Empleados", "empleados.gestion"),
                ("Administrar NFC", "empleados.nfc"),
                ("Gestionar Usuarios", "empleados.usuarios")
            ],
            "Nómina": [
                ("Generar Prenómina", "nomina.prenomina"),
                ("Control de Asistencias", "nomina.asistencias")
            ],
            "Períodos": [
                ("Gestionar Períodos", "periodos.gestion")
            ],
            "Préstamos": [
                ("Gestionar Préstamos", "prestamos.gestion")
            ],
            "Reportes": [
                ("Ver Reportes", "reportes.ver")
            ],
            "Mantenimiento": [
                ("Gestión del Sistema", "mantenimiento.gestion")
            ]
        }
        
        # Obtener permisos asignados
        permisos_asignados = self.obtener_permisos_usuario(True)
        
        # Crear un frame para cada módulo principal
        row_counter = 0
        for modulo_nombre, submodulos in modulos.items():
            # Frame para el módulo
            modulo_frame = ttk.LabelFrame(permisos_frame, text=modulo_nombre, padding="5")
            modulo_frame.pack(fill=tk.X, pady=5)
            
            # Encabezados
            ttk.Label(modulo_frame, text="Funcionalidad", width=30, font=('Helvetica', 9, 'bold'), foreground="#2596be").grid(row=0, column=0, padx=5, pady=5)
            ttk.Label(modulo_frame, text="Sin Acceso", width=10, font=('Helvetica', 9, 'bold')).grid(row=0, column=1, padx=5, pady=5)
            ttk.Label(modulo_frame, text="Personal", width=10, font=('Helvetica', 9, 'bold')).grid(row=0, column=2, padx=5, pady=5)
            ttk.Label(modulo_frame, text="Global", width=10, font=('Helvetica', 9, 'bold')).grid(row=0, column=3, padx=5, pady=5)
            
            # Crear radio buttons para cada submódulo
            for i, (nombre, codigo) in enumerate(submodulos, start=1):
                ttk.Label(modulo_frame, text=nombre).grid(row=i, column=0, padx=5, pady=5, sticky='w')
                
                var = tk.StringVar(value="sin_acceso")  # Por defecto sin acceso
                
                # Determinar el alcance actual
                permiso_actual = next((p for p in permisos_asignados if p['codigo'] == codigo), None)
                if permiso_actual:
                    var.set(permiso_actual['alcance'].lower())
                
                self.submodulos_vars[codigo] = var
                
                ttk.Radiobutton(modulo_frame, value="sin_acceso", variable=var).grid(row=i, column=1, padx=5, pady=5)
                ttk.Radiobutton(modulo_frame, value="personal", variable=var).grid(row=i, column=2, padx=5, pady=5)
                ttk.Radiobutton(modulo_frame, value="global", variable=var).grid(row=i, column=3, padx=5, pady=5)
                
            row_counter += len(submodulos) + 1
        
        # Frame para botones
        button_frame = ttk.Frame(scroll_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        guardar_btn = tk.Button(
        button_frame,
        text="Guardar Permisos",
        font=("Arial", 10, "bold"),
        fg="#ffffff",
        bg="#2596be",
        activebackground="#1e7aa3", 
        activeforeground="#ffffff",
        relief="flat",
        cursor="hand2",
        width=15,
        pady=8,
        command=self.guardar_permisos
        )
        guardar_btn.pack(pady=10)

        # Botón Cancelar 
        cancelar_btn = tk.Button(
        button_frame,
        text="Cancelar",  
        font=("Arial", 10),
        fg="#666666",
        bg="#ffffff",
        activebackground="#f0f0f0",
        relief="flat",
        cursor="hand2",
        width=15,
        pady=8,
        command=self.destroy
        )
        cancelar_btn.pack()
        
        # Hacer la ventana modal
        self.transient(parent)
        self.grab_set()
        
    def obtener_info_usuario(self):
        """Obtener información básica del usuario"""
        query = """
        SELECT u.usuario, u.rol, CONCAT(e.nombre, ' ', e.apellido) as nombre
        FROM usuarios u
        LEFT JOIN empleados e ON u.id_empleado = e.id_empleado
        WHERE u.id_usuario = %s
        """
        try:
            return self.db_manager.ejecutar_query(query, (self.id_usuario,), fetchone=True, dictionary=True)
        except Exception as e:
            print(f"Error al obtener información del usuario: {e}")
            return None
            
    def obtener_permisos_usuario(self, incluir_alcance=False):
            """
            Obtener los permisos actuales del usuario
            
            Args:
                incluir_alcance (bool): Si es True, devuelve diccionario con código y alcance. Default False.
                
            Returns:
                list: Lista de códigos de permiso o diccionarios con código y alcance
            """
            query = """
            SELECT ps.codigo, up.alcance
            FROM permisos_sistema ps
            JOIN usuario_permisos up ON ps.id_permiso = up.id_permiso
            WHERE up.id_usuario = %s
            """
            try:
                if incluir_alcance:
                    return self.db_manager.ejecutar_query(query, (self.id_usuario,), dictionary=True)
                else:
                    resultados = self.db_manager.ejecutar_query(query, (self.id_usuario,))
                    return [r[0] for r in resultados]
            except Exception as e:
                print(f"Error al obtener permisos: {e}")
                return []
    
    def guardar_permisos(self):
            """Guardar los permisos seleccionados con su alcance"""
            try:
                # Primero eliminar todos los permisos actuales
                query_delete = """
                DELETE FROM usuario_permisos
                WHERE id_usuario = %s
                """
                self.db_manager.ejecutar_query(query_delete, (self.id_usuario,), commit=True)
                
                # Obtener todos los permisos del sistema
                todos_permisos = self.db_manager.obtener_permisos_sistema()
                
                # Para cada submódulo con acceso, asignar el permiso con el alcance seleccionado
                for codigo, var in self.submodulos_vars.items():
                    alcance = var.get()
                    if alcance != "sin_acceso":
                        # Buscar el permiso correspondiente
                        permiso = next((p for p in todos_permisos if p['codigo'] == codigo), None)
                        if permiso:
                            query_insert = """
                            INSERT INTO usuario_permisos (id_usuario, id_permiso, alcance, asignado_por)
                            VALUES (%s, %s, %s, %s)
                            """
                            self.db_manager.ejecutar_query(
                                query_insert,
                                (self.id_usuario, permiso['id_permiso'], alcance.upper(), "admin"),
                                commit=True)
                # Preparar el detalle de los cambios
                permisos_modificados = []
                for codigo, var in self.submodulos_vars.items():
                    alcance = var.get()
                    if alcance != "sin_acceso":
                        permisos_modificados.append(f"{codigo}: {alcance}")

                # Registrar en auditoría
                detalle = (f"Actualización de permisos de usuario:\n"
                        f"ID Usuario: {self.id_usuario}\n"
                        f"Permisos asignados:\n" + 
                        "\n".join(permisos_modificados))

                self.db_manager.registrar_auditoria(
                    usuario=f"{self.parent.usuario_actual['nombre']} {self.parent.usuario_actual['apellido']}",
                    rol=f"{self.parent.usuario_actual['rol']}",
                    accion='Actualizó Permisos',
                    tabla='usuario_permisos',
                    detalle=detalle)
                
                messagebox.showinfo("Éxito", "Permisos actualizados correctamente")
                self.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar permisos: {str(e)}")

class GestionUsuariosForm(ttk.Frame):
    def __init__(self, parent, db_manager, usuario_actual):
        super().__init__(parent)
        self.db_manager = db_manager
        self.sistema_ayuda = Ayuda()
        self.usuario_actual = usuario_actual

        self.bind_all("<F1>", self.mostrar_ayuda)
        
        self.pack(fill=tk.BOTH, expand=True)

        # Verificar permisos
        alcance = self.db_manager.verificar_permiso(
            usuario_actual['id_usuario'], 
            'empleados.usuarios'
        )

        if not alcance or alcance != 'GLOBAL':
            messagebox.showerror("Error", "No tienes los permisos suficientes para ingresar a este módulo.")
            self.destroy()
            return
        
        # Frame principal
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Titulo
        ttk.Label(main_frame, text="Lista de Usuarios", font=('Helvetica', 12, 'bold')).pack(anchor='w', pady=(0,5))
        
        # Frame de búsqueda
        search_frame = ttk.LabelFrame(main_frame, text="Búsqueda de Usuario", padding="5")
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(search_frame, text="Estado:").pack(side=tk.LEFT, padx=5)
        self.estado_var = tk.StringVar(value="Todos")
        estado_combo = ttk.Combobox(search_frame, textvariable=self.estado_var,
                                  values=["Todos", "Activo", "Bloqueado", "Inactivo"],
                                  state="readonly", width=15)
        estado_combo.pack(side=tk.LEFT, padx=5)
        
        # Frame para el Treeview
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Crear Treeview sin el ID
        self.tree = ttk.Treeview(tree_frame, columns=(
            "id", "empleado", "usuario", "rol", "estado", "ultimo_acceso", "intentos"
        ), show='headings')
        
        # Configurar encabezados
        self.tree.heading("id", text="ID")
        self.tree.heading("empleado", text="Empleado")
        self.tree.heading("usuario", text="Usuario")
        self.tree.heading("rol", text="Rol")
        self.tree.heading("estado", text="Estado")
        self.tree.heading("ultimo_acceso", text="Último Acceso")
        self.tree.heading("intentos", text="Intentos Fallidos")
        
        # Configurar columnas
        self.tree.column("id", width=0, stretch=False)
        self.tree.column("empleado", width=200)
        self.tree.column("usuario", width=100)
        self.tree.column("rol", width=100)
        self.tree.column("estado", width=100)
        self.tree.column("ultimo_acceso", width=150)
        self.tree.column("intentos", width=100)
        
        # Configurar scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar Treeview y Scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame para botones de acción
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Centrar botones
        center_buttons = ttk.Frame(buttons_frame)
        center_buttons.pack(pady=5)
        
        ttk.Button(center_buttons, text="Desbloquear Usuario",
                  command=self.desbloquear_usuario).pack(side=tk.LEFT, padx=5)
        ttk.Button(center_buttons, text="Restablecer Usuario",
                  command=self.reestablecer_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(center_buttons, text="Cambiar Estado",
                  command=self.cambiar_estado).pack(side=tk.LEFT, padx=5)
        ttk.Button(center_buttons, text="Gestionar Permisos",
                    command=self.gestionar_permisos).pack(side=tk.LEFT, padx=5)
        ttk.Button(center_buttons, text="Ver Historial",
                  command=self.ver_historial).pack(side=tk.LEFT, padx=5)
        ttk.Button(center_buttons, text="Actualizar",
                  command=self.cargar_usuarios).pack(side=tk.LEFT, padx=5)
        
        # Configurar tags de colores
        self.tree.tag_configure('bloqueado', background='#ffcccb')
        self.tree.tag_configure('inactivo', background='#d3d3d3')
        
        # Configurar eventos
        self.search_var.trace('w', lambda *args: self.filtrar_usuarios())
        self.estado_var.trace('w', lambda *args: self.filtrar_usuarios())
        
        # Cargar usuarios
        self.cargar_usuarios()

    def mostrar_ayuda(self, event=None):
        """Muestra la ayuda contextual del módulo de empleados"""
        self.sistema_ayuda.mostrar_ayuda('usuarios')
    
    def cargar_usuarios(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        query = """
        SELECT u.id_usuario, CONCAT(e.nombre, ' ', e.apellido) as empleado,
               u.usuario, u.rol, u.estado, 
               u.ultimo_acceso, u.intentos_fallidos
        FROM usuarios u
        JOIN empleados e ON u.id_empleado = e.id_empleado
        ORDER BY u.estado, empleado
        """
        
        try:
            usuarios = self.db_manager.ejecutar_query(query, dictionary=True)
            for usuario in usuarios:
                self.tree.insert('', 'end',
                    values=(
                        usuario['id_usuario'],
                        usuario['empleado'],
                        usuario['usuario'],
                        usuario['rol'],
                        usuario['estado'],
                        usuario['ultimo_acceso'].strftime('%d-%m-%Y %H:%M:%S') if usuario['ultimo_acceso'] else 'Nunca',
                        usuario['intentos_fallidos']
                    ),
                    tags=(usuario['estado'].lower(),)
                )
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar usuarios: {str(e)}")
    
    def filtrar_usuarios(self):
        texto = self.search_var.get().lower()
        estado = self.estado_var.get()
        
        # Limpiar Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            query = """
            SELECT u.id_usuario, CONCAT(e.nombre, ' ', e.apellido) as empleado,
                u.usuario, u.rol, u.estado, 
                u.ultimo_acceso, u.intentos_fallidos
            FROM usuarios u
            JOIN empleados e ON u.id_empleado = e.id_empleado
            ORDER BY u.estado, empleado
            """
            usuarios = self.db_manager.ejecutar_query(query, dictionary=True)
            
            for usuario in usuarios:
                # Verificar filtros de búsqueda y estado
                valores = [
                    usuario['id_usuario'],
                    usuario['empleado'],
                    usuario['usuario'],
                    usuario['rol'],
                    usuario['estado'],
                    usuario['ultimo_acceso'].strftime('%Y-%m-%d %H:%M:%S') if usuario['ultimo_acceso'] else 'Nunca',
                    usuario['intentos_fallidos']
                ]
                
                if (estado == "Todos" or estado.lower() == usuario['estado'].lower()) and \
                any(str(valor).lower().find(texto) >= 0 for valor in valores):
                    self.tree.insert('', 'end', values=valores, tags=(usuario['estado'].lower(),))
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al filtrar usuarios: {str(e)}")
    
    def desbloquear_usuario(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un usuario")
            return
            
        item = self.tree.item(selected[0])
        if item['values'][4].lower() != 'bloqueado':
            messagebox.showinfo("Info", "Este usuario no está bloqueado")
            return
            
        if messagebox.askyesno("Confirmar", "¿Desea desbloquear este usuario?"):
            try:
                query = """
                UPDATE usuarios 
                SET estado = 'activo', intentos_fallidos = 0 
                WHERE id_usuario = %s
                """
                self.db_manager.ejecutar_query(query, (item['values'][0],), commit=True)
                # Detalles para auditoria
                detalle = (f"Usuario ID: {item['values'][0]} desbloqueado.\n"
                        f"Usuario: {item['values'][2]}\n"
                        f"Empleado: {item['values'][1]}")
                # Registrar auditoria
                self.db_manager.registrar_auditoria(
                    usuario=f"{self.usuario_actual['nombre']} {self.usuario_actual['apellido']}",
                    rol=f"{self.usuario_actual['rol']}",
                    accion='Desbloqueó usuario',
                    tabla='usuarios',
                    detalle=detalle)

                messagebox.showinfo("Éxito", "Usuario desbloqueado correctamente")
                self.cargar_usuarios()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def reestablecer_password(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un usuario")
            return
            
        if messagebox.askyesno("Confirmar", "¿Desea restablecer el usuario? El usuario deberá configurar su clave y preguntas en su próximo inicio de sesión"):
            try:
                item = self.tree.item(selected[0])
                usuario = str(item['values'][2])
                
                # Establecer la cédula como contraseña temporal
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(usuario.encode('utf-8'), salt)
                
                query = """
                UPDATE usuarios 
                SET contraseña = %s, primer_ingreso = TRUE 
                WHERE id_usuario = %s
                """
                self.db_manager.ejecutar_query(query, 
                    (hashed.decode('utf-8'), item['values'][0]), 
                    commit=True)
                # Detalles para auditoria
                detalle = (f"Contraseña reestablecida para:\n"
                        f"Usuario ID: {item['values'][0]}\n"
                        f"Usuario: {item['values'][2]}\n" 
                        f"Empleado: {item['values'][1]}\n"
                        "Se estableció nueva contraseña temporal")
                # Registrar auditoria
                self.db_manager.registrar_auditoria(
                    usuario=f"{self.usuario_actual['nombre']} {self.usuario_actual['apellido']}",
                    rol=f"{self.usuario_actual['rol']}",
                    accion='Restableció contraseña', 
                    tabla='usuarios',
                    detalle=detalle)           
                
                messagebox.showinfo("Éxito", f"Contraseña reestablecida.\nNueva contraseña temporal: {usuario}")
                self.cargar_usuarios()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def cambiar_estado(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un usuario")
            return
            
        item = self.tree.item(selected[0])
        estado_actual = item['values'][4].lower()
        
        # Crear diálogo
        dialog = tk.Toplevel(self)
        dialog.title("Cambiar Estado de Usuario")
        dialog.geometry("500x600")
        dialog.transient(self)
        dialog.grab_set()
        
        # Frame principal con padding
        main_container = ttk.Frame(dialog)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Título y subtítulo
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Label(
            title_frame,
            text="Cambio de Estado", 
            font=("Arial", 16, "bold"),
            foreground="#2596be"
        ).pack()

        ttk.Label(
            title_frame,
            text="Por favor complete la siguiente información",
            font=("Arial", 10),
            foreground="#666666",
            wraplength=400
        ).pack(pady=(5,15))

        # Frame principal formulario
        form_frame = ttk.LabelFrame(main_container, text="Información del Cambio", padding="15")
        form_frame.pack(fill=tk.X, pady=10, padx=20)

        # Info usuario
        ttk.Label(form_frame, text="Usuario:", font=("Arial", 10, "bold")).pack(anchor="w")
        ttk.Label(form_frame, text=item['values'][2], foreground="#666666").pack(anchor="w", pady=(0,10))

        ttk.Label(form_frame, text="Nombre:", font=("Arial", 10, "bold")).pack(anchor="w") 
        ttk.Label(form_frame, text=item['values'][1], foreground="#666666").pack(anchor="w", pady=(0,10))

        ttk.Label(form_frame, text="Estado Actual:", font=("Arial", 10, "bold")).pack(anchor="w")
        ttk.Label(form_frame, text=estado_actual.capitalize(), foreground="#666666").pack(anchor="w", pady=(0,10))

        # Estados disponibles
        ttk.Label(form_frame, text="Nuevo Estado:", font=("Arial", 10, "bold")).pack(anchor="w")
        estados = ["activo", "inactivo"]
        if estado_actual in estados:
            estados.remove(estado_actual)
            
        estado_var = tk.StringVar()
        for estado in estados:
            ttk.Radiobutton(
                form_frame, 
                text=estado.capitalize(),
                variable=estado_var,
                value=estado
            ).pack(anchor="w", padx=20, pady=2)
        estado_var.set(estados[0] if estados else "")

        # Motivo
        ttk.Label(form_frame, text="Motivo del Cambio:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10,0))
        motivo_text = tk.Text(form_frame, height=4, width=50)
        motivo_text.pack(fill=tk.X, pady=(5,10))

        # Frame botones
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=(20,0))

        # Botones estilizados
        confirmar_btn = tk.Button(
            button_frame,
            text="Confirmar Cambio",
            font=("Arial", 10, "bold"),
            fg="#ffffff",
            bg="#2596be", 
            activebackground="#1e7aa3",
            relief="flat",
            cursor="hand2",
            command=lambda: confirmar()
        )
        confirmar_btn.pack(pady=10)

        cancelar_btn = tk.Button(
            button_frame,
            text="Cancelar",
            font=("Arial", 10),
            fg="#666666",
            bg="#ffffff",
            activebackground="#f0f0f0",
            relief="flat", 
            cursor="hand2",
            command=dialog.destroy
        )
        cancelar_btn.pack()

        def confirmar():
            if not estado_var.get() or not motivo_text.get("1.0", tk.END).strip():
                messagebox.showwarning("Advertencia", "Todos los campos son requeridos")
                return
                
            try:
                query = """
                UPDATE usuarios 
                SET estado = %s 
                WHERE id_usuario = %s
                """
                self.db_manager.ejecutar_query(query, 
                    (estado_var.get(), item['values'][0]), 
                    commit=True)
                
                # Registrar en el historial
                self.registrar_cambio_estado(
                    item['values'][0],
                    estado_actual,
                    estado_var.get(),
                    motivo_text.get("1.0", tk.END).strip())

                # Registrar en auditoría 
                detalle = (f"Cambio de estado de usuario:\n"
                        f"ID: {item['values'][0]}\n"
                        f"Usuario: {item['values'][2]}\n"
                        f"Empleado: {item['values'][1]}\n"
                        f"Estado anterior: {estado_actual}\n"
                        f"Nuevo estado: {estado_var.get()}\n"
                        f"Motivo: {motivo_text.get('1.0', tk.END).strip()}")

                self.db_manager.registrar_auditoria(
                    usuario=f"{self.usuario_actual['nombre']} {self.usuario_actual['apellido']}",
                    rol=f"{self.usuario_actual['rol']}",
                    accion='Cambió status',
                    tabla='usuarios',
                    detalle=detalle)

                messagebox.showinfo("Éxito", "Estado actualizado correctamente")
                dialog.destroy()
                self.cargar_usuarios()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        # Centrar diálogo
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def registrar_cambio_estado(self, id_usuario, estado_anterior, estado_nuevo, motivo):
        query = """
        INSERT INTO historial_usuarios 
        (id_usuario, estado_anterior, estado_nuevo, motivo, fecha_cambio)
        VALUES (%s, %s, %s, %s, NOW())
        """
        self.db_manager.ejecutar_query(query, 
            (id_usuario, estado_anterior, estado_nuevo, motivo),
            commit=True
        )
    
    def ver_historial(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un usuario")
            return
            
        item = self.tree.item(selected[0])
        id_usuario = item['values'][0]
        
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title(f"Historial de Usuario: {item['values'][1]}")
        dialog.geometry("600x400")
        
        # Create Treeview
        tree = ttk.Treeview(dialog, columns=(
            "fecha", "estado_anterior", "estado_nuevo", "motivo"
        ), show='headings')
        
        tree.heading("fecha", text="Fecha")
        tree.heading("estado_anterior", text="Estado Anterior")
        tree.heading("estado_nuevo", text="Nuevo Estado")
        tree.heading("motivo", text="Motivo")
        
        tree.column("fecha", width=150)
        tree.column("estado_anterior", width=100)
        tree.column("estado_nuevo", width=100)
        tree.column("motivo", width=200)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load history
        query = """
        SELECT fecha_cambio, estado_anterior, estado_nuevo, motivo
        FROM historial_usuarios
        WHERE id_usuario = %s
        ORDER BY fecha_cambio DESC
        """
        try:
            historial = self.db_manager.ejecutar_query(query, (id_usuario,))
            for registro in historial:
                tree.insert('', 'end', values=registro)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar historial: {str(e)}")

    def gestionar_permisos(self):
        """Abrir ventana de gestión de permisos"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un usuario")
            return
            
        item = self.tree.item(selected[0])
        id_usuario = item['values'][0]
        GestionPermisosForm(self, self.db_manager, id_usuario)