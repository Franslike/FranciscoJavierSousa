import tkinter as tk
from tkinter import ttk, messagebox
import bcrypt
from datetime import datetime

class GestionUsuariosForm(ttk.Frame):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        
        self.pack(fill=tk.BOTH, expand=True)
        
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
        ttk.Button(center_buttons, text="Reestablecer Contraseña",
                  command=self.reestablecer_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(center_buttons, text="Cambiar Estado",
                  command=self.cambiar_estado).pack(side=tk.LEFT, padx=5)
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
                        usuario['ultimo_acceso'].strftime('%Y-%m-%d %H:%M:%S') if usuario['ultimo_acceso'] else 'Nunca',
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
                messagebox.showinfo("Éxito", "Usuario desbloqueado correctamente")
                self.cargar_usuarios()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def reestablecer_password(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un usuario")
            return
            
        if messagebox.askyesno("Confirmar", 
                            "¿Desea reestablecer la contraseña? El usuario deberá cambiarla en su próximo inicio de sesión"):
            try:
                item = self.tree.item(selected[0])
                usuario = item['values'][2]
                
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
                    commit=True
                )
                
                messagebox.showinfo("Éxito", 
                    f"Contraseña reestablecida.\nNueva contraseña temporal: {usuario}")
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
        
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title("Cambiar Estado")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="Nuevo estado:").pack(pady=5)
        estado_var = tk.StringVar()
        estados = ["activo", "inactivo"]
        if estado_actual in estados:
            estados.remove(estado_actual)
            
        estado_combo = ttk.Combobox(dialog, textvariable=estado_var,
                                  values=estados, state="readonly")
        estado_combo.pack(pady=5)
        
        ttk.Label(dialog, text="Motivo:").pack(pady=5)
        motivo_text = tk.Text(dialog, height=3)
        motivo_text.pack(pady=5, padx=10)
        
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
                    commit=True
                )
                
                # Register in history
                self.registrar_cambio_estado(
                    item['values'][0],
                    estado_actual,
                    estado_var.get(),
                    motivo_text.get("1.0", tk.END).strip()
                )
                
                messagebox.showinfo("Éxito", "Estado actualizado correctamente")
                dialog.destroy()
                self.cargar_usuarios()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(dialog, text="Confirmar", command=confirmar).pack(pady=10)
        ttk.Button(dialog, text="Cancelar", command=dialog.destroy).pack()
    
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