import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, date
import traceback

class EmpleadoDetallesForm(ttk.Frame):
    """Formulario para ver/editar detalles del empleado"""
    def __init__(self, parent, db_manager, empleado_id):
        super().__init__(parent)
        self.db_manager = db_manager
        self.empleado_id = empleado_id
        
        # Configuración básica
        self.title("Detalles del Empleado")
        self.geometry("600x700")
        
        # Frame principal
        self.main_frame = ttk.Frame(self, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame para los campos
        self.campos_frame = ttk.Frame(self.main_frame)
        self.campos_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Diccionario para almacenar las entradas
        self.entradas = {}
        
        # Crear campos
        self.crear_campos()
        
        # Frame para botones
        self.botones_frame = ttk.Frame(self.main_frame)
        self.botones_frame.pack(fill=tk.X, pady=20)
        
        # Botones
        self.btn_editar = ttk.Button(self.botones_frame, text="Editar",
                                   command=self.activar_edicion)
        self.btn_editar.pack(side=tk.LEFT, padx=5)
        
        self.btn_guardar = ttk.Button(self.botones_frame, text="Guardar",
                                    command=self.guardar_cambios, state='disabled')
        self.btn_guardar.pack(side=tk.LEFT, padx=5)
        
        self.btn_cancelar = ttk.Button(self.botones_frame, text="Cancelar",
                                     command=self.cancelar_edicion, state='disabled')
        self.btn_cancelar.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(self.botones_frame, text="Cerrar",
                  command=self.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Cargar datos del empleado
        self.cargar_datos()
        
    def crear_campos(self):
        """Crear los campos del formulario"""
        campos = [
            ("Nombre:", "nombre", "readonly"),
            ("Apellido:", "apellido", "readonly"),
            ("Cédula:", "cedula", "readonly"),
            ("Dirección:", "direccion", "editable"),
            ("Fecha de Nacimiento:", "fecha_nacimiento", "date_readonly"),
            ("Cargo:", "cargo", "editable"),
            ("Salario:", "salario", "editable"),
            ("Fecha de Contratación:", "fecha_contratacion", "date_readonly"),
            ("Status:", "status", "readonly")
        ]
        
        for i, campo in enumerate(campos):
            label = campo[0]
            key = campo[1]
            tipo = campo[2]
            
            ttk.Label(self.campos_frame, text=label).grid(
                row=i, column=0, sticky='e', padx=5, pady=5)
            
            if tipo.startswith("date"):
                widget = DateEntry(self.campos_frame, width=20, state='disabled')
            else:
                widget = ttk.Entry(self.campos_frame, width=40, state='disabled')
                
            widget.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
            self.entradas[key] = widget
        
        # Frame para dispositivos NFC
        current_row = len(campos)
        nfc_frame = ttk.LabelFrame(self.campos_frame, text="Dispositivos NFC", padding="5")
        nfc_frame.grid(row=current_row, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        
        # Crear Treeview para dispositivos NFC
        self.nfc_tree = ttk.Treeview(nfc_frame, columns=("tipo", "uid", "estado"), height=3, show='headings')
        
        # Configurar columnas
        self.nfc_tree.heading("tipo", text="Tipo")
        self.nfc_tree.heading("uid", text="UID")
        self.nfc_tree.heading("estado", text="Estado")
        
        self.nfc_tree.column("tipo", width=100)
        self.nfc_tree.column("uid", width=200)
        self.nfc_tree.column("estado", width=100)
        
        self.nfc_tree.pack(fill=tk.X, padx=5, pady=5)
        
        # Frame para botones de NFC
        nfc_buttons_frame = ttk.Frame(nfc_frame)
        nfc_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(nfc_buttons_frame, text="Agregar Tarjeta",
                command=self.agregar_tarjeta).pack(side=tk.LEFT, padx=5)
        ttk.Button(nfc_buttons_frame, text="Agregar Teléfono",
                command=self.agregar_telefono).pack(side=tk.LEFT, padx=5)
        ttk.Button(nfc_buttons_frame, text="Remover Dispositivo",
                command=self.remover_dispositivo).pack(side=tk.LEFT, padx=5)
            
        # Hacer que la columna de entrada se expanda
        self.campos_frame.grid_columnconfigure(1, weight=1)
    
    def cargar_datos(self):
        """Cargar los datos del empleado"""
        try:
            empleado = self.db_manager.obtener_empleado(self.empleado_id)
            
            if empleado:
                # Nombre
                self.entradas["nombre"].configure(state='normal')
                self.entradas["nombre"].delete(0, tk.END)
                self.entradas["nombre"].insert(0, empleado['nombre'])
                self.entradas["nombre"].configure(state='disabled')
                
                # Apellido
                self.entradas["apellido"].configure(state='normal')
                self.entradas["apellido"].delete(0, tk.END)
                self.entradas["apellido"].insert(0, empleado['apellido'])
                self.entradas["apellido"].configure(state='disabled')
                
                # Cédula
                self.entradas["cedula"].configure(state='normal')
                self.entradas["cedula"].delete(0, tk.END)
                self.entradas["cedula"].insert(0, empleado['cedula'])
                self.entradas["cedula"].configure(state='disabled')
                
                # Dirección
                self.entradas["direccion"].configure(state='normal')
                self.entradas["direccion"].delete(0, tk.END)
                self.entradas["direccion"].insert(0, empleado['direccion'])
                self.entradas["direccion"].configure(state='disabled')
                
                # Cargo
                self.entradas["cargo"].configure(state='normal')
                self.entradas["cargo"].delete(0, tk.END)
                self.entradas["cargo"].insert(0, empleado['cargo'])
                self.entradas["cargo"].configure(state='disabled')
                
                # Salario
                self.entradas["salario"].configure(state='normal')
                self.entradas["salario"].delete(0, tk.END)
                self.entradas["salario"].insert(0, f"{float(empleado['salario']):,.2f}")
                self.entradas["salario"].configure(state='disabled')
                
                # Status
                self.entradas["status"].configure(state='normal')
                self.entradas["status"].delete(0, tk.END)
                self.entradas["status"].insert(0, empleado['status'])
                self.entradas["status"].configure(state='disabled')
                
                # Fecha de Nacimiento
                if empleado['fecha_nacimiento']:
                    self.entradas["fecha_nacimiento"].configure(state='normal')
                    self.entradas["fecha_nacimiento"].set_date(empleado['fecha_nacimiento'])
                    self.entradas["fecha_nacimiento"].configure(state='disabled')
                
                # Fecha de Contratación
                if empleado['fecha_contratacion']:
                    self.entradas["fecha_contratacion"].configure(state='normal')
                    self.entradas["fecha_contratacion"].set_date(empleado['fecha_contratacion'])
                    self.entradas["fecha_contratacion"].configure(state='disabled')
                
                # Cargar dispositivos NFC
                dispositivos = self.db_manager.obtener_dispositivos_empleado(self.empleado_id)
                
                # Limpiar Treeview de NFC
                for item in self.nfc_tree.get_children():
                    self.nfc_tree.delete(item)
                
                # Insertar dispositivos
                for dispositivo in dispositivos:
                    self.nfc_tree.insert('', 'end', values=(
                        dispositivo['tipo'],
                        dispositivo['uid'],
                        dispositivo['estado']
                    ))
                    
            else:
                messagebox.showerror("Error", "No se encontraron datos del empleado")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")

    def agregar_tarjeta(self):
        """Agregar una nueva tarjeta NFC al empleado"""
        # Crear ventana de diálogo
        dialog = tk.Toplevel(self)
        dialog.title("Agregar Tarjeta NFC")
        dialog.geometry("400x200")
        dialog.grab_set()
        
        # Frame principal
        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Combobox para tarjetas disponibles
        ttk.Label(frame, text="Seleccione una tarjeta:").pack(pady=5)
        tarjetas_combo = ttk.Combobox(frame, state="readonly")
        tarjetas_combo.pack(pady=5, fill=tk.X)
        
        # Cargar tarjetas disponibles
        tarjetas = self.db_manager.obtener_tarjetas_disponibles()
        if tarjetas:
            tarjetas_combo['values'] = [f"{t[0]} - {t[1]}" for t in tarjetas]
        else:
            tarjetas_combo['values'] = ["No hay tarjetas disponibles"]
        
        def confirmar():
            if not tarjetas_combo.get() or tarjetas_combo.get() == "No hay tarjetas disponibles":
                messagebox.showwarning("Advertencia", "Por favor seleccione una tarjeta válida")
                return
            
            id_dispositivo = tarjetas_combo.get().split(' - ')[0]
            try:
                self.db_manager.asignar_dispositivo(self.empleado_id, id_dispositivo)
                messagebox.showinfo("Éxito", "Tarjeta asignada correctamente")
                self.cargar_datos()  # Recargar datos
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error al asignar tarjeta: {str(e)}")
        
        ttk.Button(frame, text="Confirmar", command=confirmar).pack(pady=10)
        ttk.Button(frame, text="Cancelar", command=dialog.destroy).pack(pady=5)

    def agregar_telefono(self):
        """Agregar un teléfono como dispositivo NFC"""
        # Crear ventana de diálogo
        dialog = tk.Toplevel(self)
        dialog.title("Agregar Teléfono NFC")
        dialog.geometry("400x200")
        dialog.grab_set()
        
        # Frame principal
        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Campo para UID
        ttk.Label(frame, text="UID del teléfono:").pack(pady=5)
        uid_entry = ttk.Entry(frame)
        uid_entry.pack(pady=5, fill=tk.X)
        
        # Nota informativa
        ttk.Label(frame, 
                text="Ingrese el UID en formato hexadecimal (ej: 1A2B3C4D)",
                foreground="gray").pack(pady=5)
        
        def confirmar():
            uid = uid_entry.get().strip().upper()
            if not uid:
                messagebox.showwarning("Advertencia", "Por favor ingrese el UID")
                return
                
            if not all(c in '0123456789ABCDEF' for c in uid):
                messagebox.showerror("Error", "El UID debe estar en formato hexadecimal")
                return
                
            try:
                # Primero registrar el dispositivo
                id_dispositivo = self.db_manager.registrar_telefono(uid)
                # Luego asignarlo al empleado
                self.db_manager.asignar_dispositivo(self.empleado_id, id_dispositivo)
                messagebox.showinfo("Éxito", "Teléfono registrado y asignado correctamente")
                self.cargar_datos()  # Recargar datos
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error al registrar teléfono: {str(e)}")
        
        ttk.Button(frame, text="Confirmar", command=confirmar).pack(pady=10)
        ttk.Button(frame, text="Cancelar", command=dialog.destroy).pack(pady=5)

    def remover_dispositivo(self):
        """Remover un dispositivo NFC seleccionado"""
        selected = self.nfc_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un dispositivo")
            return
            
        item = self.nfc_tree.item(selected[0])
        tipo = item['values'][0]
        uid = item['values'][1]
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro de remover este {tipo}?"):
            try:
                self.db_manager.desasignar_dispositivo(self.empleado_id, uid)
                messagebox.showinfo("Éxito", "Dispositivo removido correctamente")
                self.cargar_datos()  # Recargar datos
            except Exception as e:
                messagebox.showerror("Error", f"Error al remover dispositivo: {str(e)}")
    
    def activar_edicion(self):
        """Activar la edición solo de campos permitidos"""
        # Lista de campos que no se pueden editar
        campos_no_editables = [
            "nombre", "apellido", "cedula", "fecha_nacimiento", 
            "fecha_contratacion", "status"
        ]
        
        # Configurar el campo de cargo como Combobox cuando se activa la edición
        cargo_actual = self.entradas["cargo"].get()
        self.entradas["cargo"].grid_forget()  # Remover el Entry actual
        
        # Crear y configurar el Combobox para cargo
        self.combo_cargo = ttk.Combobox(
            self.campos_frame, 
            values=["Gerente", "Supervisor", "Analista", "Empleado"],
            state="readonly"
        )
        self.combo_cargo.grid(row=5, column=1, sticky='ew', padx=5, pady=5)  # Ajusta row según tu layout
        self.combo_cargo.set(cargo_actual)
        self.entradas["cargo"] = self.combo_cargo
        
        # Activar solo los campos editables
        for key, widget in self.entradas.items():
            if key not in campos_no_editables:
                if key == "cargo":
                    continue  # Ya lo manejamos arriba
                else:
                    widget.config(state='normal')
        
        # Configurar estado de los botones
        self.btn_editar.config(state='disabled')
        self.btn_guardar.config(state='normal')
        self.btn_cancelar.config(state='normal')
    
    def desactivar_edicion(self):
        """Desactivar la edición y volver a los Entry normales"""
        # Restaurar el campo de cargo a Entry
        if hasattr(self, 'combo_cargo'):
            cargo_actual = self.combo_cargo.get()
            self.combo_cargo.grid_forget()
            
            cargo_entry = ttk.Entry(self.campos_frame)
            cargo_entry.grid(row=5, column=1, sticky='ew', padx=5, pady=5)  # Ajusta row según tu layout
            cargo_entry.insert(0, cargo_actual)
            cargo_entry.config(state='disabled')
            self.entradas["cargo"] = cargo_entry
        
        # Desactivar todos los campos
        for widget in self.entradas.values():
            widget.config(state='disabled')
        
        # Configurar estado de los botones
        self.btn_editar.config(state='normal')
        self.btn_guardar.config(state='disabled')
        self.btn_cancelar.config(state='disabled')
    
    def guardar_cambios(self):
        """Guardar los cambios realizados"""
        try:
            # Recopilar datos
            datos = {
                'nombre': self.entradas["nombre"].get().strip(),
                'apellido': self.entradas["apellido"].get().strip(),
                'cargo': self.entradas["cargo"].get().strip(),
                'salario': float(self.entradas["salario"].get().replace(',', '')),
                'direccion': self.entradas["direccion"].get().strip(),
                'fecha_nacimiento': self.entradas["fecha_nacimiento"].get_date(),
                'fecha_contratacion': self.entradas["fecha_contratacion"].get_date(),
                'status': self.entradas["status"].get().strip()
            }
            
            # Validar datos
            if not all([
                datos['direccion'],
                datos['cargo'], 
                datos['salario'] > 0
            ]):
                messagebox.showwarning(
                    "Advertencia", 
                    "Los campos Dirección, Cargo y Salario son obligatorios"
                )
                return
            
            # Actualizar en la base de datos
            self.db_manager.actualizar_empleado(self.empleado_id, datos)
            
            messagebox.showinfo("Éxito", "Datos actualizados correctamente")
            self.desactivar_edicion()
            
            # Actualizar la lista de empleados en la ventana principal
            if hasattr(self.master, 'cargar_empleados'):
                self.master.cargar_empleados()
                
        except ValueError:
            messagebox.showerror("Error", "El salario debe ser un número válido")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar cambios: {str(e)}")
    
    def cancelar_edicion(self):
        """Cancelar la edición y recargar datos originales"""
        self.desactivar_edicion()
        self.cargar_datos()

class EmpleadosForm(ttk.Frame):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager

        self.pack(fill=tk.BOTH, expand=True)
        
        # Frame principal
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pestaña de Registro
        self.registro_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.registro_frame, text="Registro de Empleado")
        
        # Pestaña de Lista
        self.lista_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.lista_frame, text="Lista de Empleados")
        
        # Configurar formulario de registro
        self.registro_form()
        
        # Configurar lista de empleados
        self.lista_empleados()
        
    def registro_form(self):
        """Configurar el formulario de registro de empleados"""
        # Frame para el formulario
        form_frame = ttk.LabelFrame(self.registro_frame, text="Datos del Empleado", padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Grid para organizar los campos
        form_frame.columnconfigure(1, weight=1)
        
        # Campos del formulario
        campos = [
            ("Nombre:", "nombre_entry"),
            ("Apellido:", "apellido_entry"),
            ("Cédula:", "cedula_entry"),
            ("Dirección:", "direccion_entry"),
        ]
        
        for i, (label, attr) in enumerate(campos):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            entry = ttk.Entry(form_frame)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            setattr(self, attr, entry)

        # Fecha de Nacimiento
        current_row = len(campos)
        ttk.Label(form_frame, text="Fecha de Nacimiento:").grid(row=current_row, column=0, padx=5, pady=5, sticky="e")
        self.fecha_nacimiento = DateEntry(form_frame, width=20)
        self.fecha_nacimiento.grid(row=current_row, column=1, padx=5, pady=5, sticky="w")
        
        # Cargo (Combobox)
        current_row += 1
        ttk.Label(form_frame, text="Cargo:").grid(row=current_row, column=0, padx=5, pady=5, sticky="e")
        self.cargo_var = tk.StringVar()
        self.cargo_combo = ttk.Combobox(form_frame, textvariable=self.cargo_var, state="readonly")
        self.cargo_combo['values'] = ["Gerente", "Supervisor", "Analista", "Empleado"]
        self.cargo_combo.grid(row=current_row, column=1, padx=5, pady=5, sticky="ew")
        
        # Salario
        current_row += 1
        ttk.Label(form_frame, text="Salario:").grid(row=current_row, column=0, padx=5, pady=5, sticky="e")
        self.salario_entry = ttk.Entry(form_frame)
        self.salario_entry.grid(row=current_row, column=1, padx=5, pady=5, sticky="ew")
        
        # Fecha de Contratación
        current_row += 1
        ttk.Label(form_frame, text="Fecha de Contratación:").grid(row=current_row, column=0, padx=5, pady=5, sticky="e")
        self.fecha_contratacion = DateEntry(form_frame, width=20)
        self.fecha_contratacion.grid(row=current_row, column=1, padx=5, pady=5, sticky="w")

        # Frame para NFC
        current_row += 1
        nfc_frame = ttk.LabelFrame(form_frame, text="Dispositivos NFC", padding="5")
        nfc_frame.grid(row=current_row, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        
        # Tarjeta NFC
        ttk.Label(nfc_frame, text="Tarjeta NFC:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.uid_nfc_var = tk.StringVar()
        self.uid_nfc_combo = ttk.Combobox(nfc_frame, textvariable=self.uid_nfc_var, state="readonly")
        self.uid_nfc_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Checkbox para teléfono
        self.telefono_var = tk.BooleanVar()
        self.telefono_check = ttk.Checkbutton(nfc_frame, 
            text="Agregar teléfono como credencial", 
            variable=self.telefono_var,
            command=self.toggle_telefono_nfc)
        self.telefono_check.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
        # Frame para datos del teléfono (inicialmente oculto)
        self.telefono_frame = ttk.Frame(nfc_frame)
        self.telefono_frame.grid(row=2, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        self.telefono_frame.grid_remove()  # Oculto por defecto
        
        ttk.Label(self.telefono_frame, text="UID Teléfono:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.telefono_uid_entry = ttk.Entry(self.telefono_frame, width=40)
        self.telefono_uid_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Nota informativa sobre el formato del UID
        ttk.Label(self.telefono_frame, 
                text="Ingrese el UID del teléfono en formato hexadecimal (ej: 1A2B3C4D)",
                foreground="gray").grid(row=1, column=0, columnspan=3, padx=5, pady=(0,5), sticky="w")
        
        # Cargar UIDs disponibles
        self.cargar_uids_disponibles()

        # Frame para permisos
        permisos_frame = ttk.LabelFrame(form_frame, text="Permisos de Usuario", padding="5")
        permisos_frame.grid(row=current_row + 1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        
        # Obtener permisos disponibles
        self.permisos_vars = {}
        permisos = self.db_manager.obtener_permisos_sistema()
        
        # Crear checkboxes para cada permiso
        for i, permiso in enumerate(permisos):
            var = tk.BooleanVar()
            self.permisos_vars[permiso['codigo']] = var
            ttk.Checkbutton(permisos_frame, 
                        text=permiso['descripcion'],
                        variable=var).grid(row=i//2, 
                                            column=i%2, 
                                            padx=5, 
                                            pady=2, 
                                            sticky='w')
    
        # Frame para botones
        current_row += 1
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=current_row, column=0, columnspan=2, pady=20)
        
        # Botones
        ttk.Button(button_frame, text="Guardar", command=self.guardar_empleado).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self.limpiar_formulario).pack(side=tk.LEFT, padx=5)
        
    def lista_empleados(self):
        """Configurar la lista de empleados"""
        # Frame para la parte superior (título y búsqueda)
        top_frame = ttk.Frame(self.lista_frame)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Título a la izquierda
        ttk.Label(top_frame, text="Lista de Empleados", 
                 font=('Helvetica', 12, 'bold')).pack(side=tk.LEFT, pady=5)
        
        # Frame de búsqueda a la derecha
        search_frame = ttk.LabelFrame(top_frame, text="Búsqueda", padding=5)
        search_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Label(search_frame, text="🔍").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, 
                                    textvariable=self.search_var,
                                    width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        # Crear Treeview con columna adicional para status
        self.tree = ttk.Treeview(self.lista_frame, columns=(
            "ID", "Nombre", "Apellido", "Cedula", "Cargo", "Salario", 
            "Fecha_Contratacion", "Status"
        ), show='headings')
        
        # Configurar columnas
        for col in self.tree['columns']:
            self.tree.heading(col, text=col.replace('_', ' '))
            width = 150 if col in ['Nombre', 'Apellido', 'Cargo'] else 100
            self.tree.column(col, width=width)
        
        # Ajustar ancho de columna Status
        self.tree.column("Status", width=80)
        
        # Configurar colores para los diferentes status
        self.tree.tag_configure('inactivo', foreground='gray')
        
        # Scrollbars
        vsb = ttk.Scrollbar(self.lista_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.lista_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Frame para botones de acción (alineado a la derecha)
        button_frame = ttk.Frame(self.lista_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        # Contenedor para los botones (alineado a la derecha)
        buttons_container = ttk.Frame(button_frame)
        buttons_container.pack(side=tk.RIGHT)
        
        ttk.Button(buttons_container, text="Actualizar", 
                  command=self.cargar_empleados).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_container, text="Cambiar Status", 
                  command=self.cambiar_status_empleado).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_container, text="Editar", 
                  command=self.editar_empleado).pack(side=tk.LEFT, padx=5)
        
        # Bindings
        self.search_var.trace('w', self.filtrar_empleados)
        self.tree.bind('<Double-1>', lambda e: self.editar_empleado())
        
        # Cargar datos iniciales
        self.cargar_empleados()
        
    def guardar_empleado(self):
        """Guardar un nuevo empleado con validaciones mejoradas"""
        try:
            # Obtener valores del formulario
            nombre = self.nombre_entry.get().strip()
            apellido = self.apellido_entry.get().strip()
            cedula = self.cedula_entry.get().strip()
            cargo = self.cargo_var.get()
            salario = self.salario_entry.get().strip()
            fecha_contratacion = self.fecha_contratacion.get_date()
            direccion = self.direccion_entry.get().strip()
            fecha_nacimiento = self.fecha_nacimiento.get_date()
            
            # Validaciones mejoradas
            errores = []
            if not nombre or len(nombre) < 2:
                errores.append("El nombre debe tener al menos 2 caracteres")
            if not apellido or len(apellido) < 2:
                errores.append("El apellido debe tener al menos 2 caracteres")
            if not cedula or not cedula.isdigit():
                errores.append("La cédula debe contener solo números")
            if not cargo:
                errores.append("Debe seleccionar un cargo")
            try:
                salario = float(salario)
                if salario <= 0:
                    errores.append("El salario debe ser mayor a 0")
            except ValueError:
                errores.append("El salario debe ser un número válido")

            # Validar NFC
            if not self.uid_nfc_var.get():
                errores.append("Debe seleccionar una tarjeta NFC")
            elif self.uid_nfc_var.get() == "No hay tarjetas disponibles":
                errores.append("No hay tarjetas NFC disponibles para asignar")
            
            if self.telefono_var.get():
                uid_telefono = self.telefono_uid_entry.get().strip()
                if not uid_telefono:
                    errores.append("Debe ingresar el UID del teléfono")
                elif not all(c in '0123456789ABCDEFabcdef' for c in uid_telefono):
                    errores.append("El UID del teléfono debe estar en formato hexadecimal")
            
            if errores:
                messagebox.showerror("Error de Validación", "\n".join(errores))
                return
                
            # Verificar si ya existe el empleado (por cédula)
            if self.db_manager.verificar_empleado_existente(cedula):
                messagebox.showerror("Error", 
                                "Ya existe un empleado registrado con esta cédula")
                return

            # Verificar si el teléfono ya está registrado
            if self.telefono_var.get():
                uid_telefono = self.telefono_uid_entry.get().strip().upper()
                if self.db_manager.verificar_dispositivo_existente(uid_telefono):
                    messagebox.showerror("Error", 
                                    "El UID del teléfono ya está registrado en el sistema")
                    return
            
            # Obtener UIDs
            uid_tarjeta = self.uid_nfc_var.get().split(' - ')[0]
            uid_telefono = self.telefono_uid_entry.get().strip().upper() if self.telefono_var.get() else None
            
            # Recopilar permisos seleccionados
            permisos_seleccionados = [
                codigo for codigo, var in self.permisos_vars.items() 
                if var.get()
            ]
            
            try:
                # Registrar empleado con permisos
                self.db_manager.registrar_empleado_con_nfc(
                    nombre=self.nombre_entry.get().strip(),
                    apellido=self.apellido_entry.get().strip(),
                    cedula=self.cedula_entry.get().strip(),
                    cargo=self.cargo_var.get(),
                    salario=float(self.salario_entry.get().strip()),
                    fecha_contratacion=self.fecha_contratacion.get_date(),
                    direccion=self.direccion_entry.get().strip(),
                    fecha_nacimiento=self.fecha_nacimiento.get_date(),
                    uid_tarjeta=self.uid_nfc_var.get().split(' - ')[0] if self.uid_nfc_var.get() else None,
                    uid_telefono=self.telefono_uid_entry.get().strip().upper() if self.telefono_var.get() else None,
                    permisos=permisos_seleccionados
                )
                
                messagebox.showinfo("Éxito", 
                                "Empleado registrado correctamente.\n" +
                                f"Usuario: {self.cedula_entry.get().strip()}\n" +
                                "Contraseña inicial: La misma cédula")
                
                self.limpiar_formulario()
                self.cargar_empleados()
                # Recargar los UIDs disponibles después de registrar
                self.cargar_uids_disponibles()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al registrar empleado: {str(e)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar el formulario: {str(e)}")
    
    def limpiar_formulario(self):
        """Limpiar todos los campos del formulario"""
        self.nombre_entry.delete(0, tk.END)
        self.apellido_entry.delete(0, tk.END)
        self.cedula_entry.delete(0, tk.END)
        self.direccion_entry.delete(0, tk.END)
        self.cargo_var.set('')
        self.salario_entry.delete(0, tk.END)
        self.fecha_nacimiento.set_date(datetime.now())
        self.fecha_contratacion.set_date(datetime.now())
        self.uid_nfc_var.set('')
        self.telefono_var.set(False)
        self.telefono_uid_entry.delete(0, tk.END)
        self.telefono_frame.grid_remove()
    
    def cargar_empleados(self):
        """Cargar la lista de empleados"""
        # Limpiar Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Obtener y mostrar empleados
        empleados = self.db_manager.ver_empleados()
        for emp in empleados:
            # Formatear salario
            valores = list(emp)
            valores[5] = f"{float(valores[5]):,.2f}"  # Formato para el salario
            
            # Agregar el status a los valores
            status = valores[-1] if len(valores) > 7 else 'activo'
            if len(valores) <= 7:
                valores.append(status)
            
            # Insertar con el tag correspondiente
            self.tree.insert('', 'end', values=valores, 
                           tags=(status.lower(),))
    
    def filtrar_empleados(self, *args):
        """Filtrar empleados según el texto de búsqueda"""
        search_text = self.search_var.get().lower()
        
        # Limpiar Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener empleados
        empleados = self.db_manager.ver_empleados()
        
        # Filtrar y mostrar coincidencias
        for emp in empleados:
            if any(str(value).lower().find(search_text) >= 0 for value in emp):
                valores = list(emp)
                valores[5] = f"{float(valores[5]):,.2f}"  # Formato para el salario
                status = valores[-1] if len(valores) > 7 else 'activo'
                if len(valores) <= 7:
                    valores.append(status)
                self.tree.insert('', 'end', values=valores,
                               tags=(status.lower(),))
                
    def cargar_uids_disponibles(self):
        """Cargar los UIDs NFC disponibles en el combobox"""
        uids = self.db_manager.obtener_uids_disponibles()
        if uids:
            self.uid_nfc_combo['values'] = [f"{uid[0]} - {uid[1]}" for uid in uids]
        else:
            self.uid_nfc_combo['values'] = ["No hay tarjetas disponibles"]

    def toggle_telefono_nfc(self):
        """Mostrar u ocultar el frame de teléfono NFC"""
        if self.telefono_var.get():
            self.telefono_frame.grid()
        else:
            self.telefono_frame.grid_remove()
            self.telefono_uid_entry.delete(0, tk.END)
                
    def cambiar_status_empleado(self):
        """Cambiar el status del empleado seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un empleado")
            return
            
        # Obtener datos del empleado seleccionado
        item = self.tree.item(selected[0])
        id_empleado = item['values'][0]
        nombre_empleado = f"{item['values'][1]} {item['values'][2]}"
        status_actual = item['values'][-1]
        
        # Confirmar cambio de status
        nuevo_status = 'inactivo' if status_actual == 'activo' else 'activo'
        if messagebox.askyesno("Confirmar Cambio de Status",
                             f"¿Desea cambiar el status del empleado {nombre_empleado} a {nuevo_status}?"):
            try:
                self.db_manager.cambiar_status_empleado(id_empleado, nuevo_status)
                messagebox.showinfo("Éxito", 
                                  f"Status del empleado cambiado a {nuevo_status}")
                self.cargar_empleados()
            except Exception as e:
                messagebox.showerror("Error",
                                   f"Error al cambiar el status: {str(e)}")
    
    def editar_empleado(self):
        """Abrir formulario para editar empleado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un empleado")
            return
            
        item = self.tree.item(selected[0])
        id_empleado = item['values'][0]
        print(f"ID del empleado seleccionado: {id_empleado}")

        detalles_form = EmpleadoDetallesForm(self, self.db_manager, id_empleado)
        
        # Centrar la ventana
        detalles_form.update_idletasks()
        width = detalles_form.winfo_width()
        height = detalles_form.winfo_height()
        x = (detalles_form.winfo_screenwidth() // 2) - (width // 2)
        y = (detalles_form.winfo_screenheight() // 2) - (height // 2)
        detalles_form.geometry(f'+{x}+{y}')
        
        detalles_form.grab_set()