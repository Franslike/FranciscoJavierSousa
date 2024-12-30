import tkinter as tk
from formularios.registro_empleados_form import RegistroEmpleadoForm
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, date
import traceback

class EmpleadoDetallesForm(tk.Toplevel):
    """Formulario para ver/editar detalles del empleado"""
    def __init__(self, parent, db_manager, empleado_id):
        super().__init__(parent)
        self.db_manager = db_manager
        self.empleado_id = empleado_id
        
        # Configuración básica
        self.title("Detalles del Empleado")
        self.geometry("800x700")
        
        # Frame principal con scroll
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de contenido
        self.content_frame = ttk.Frame(self.main_frame, padding="20")
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas y scrollbar
        self.canvas = tk.Canvas(self.content_frame)
        self.scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Empaquetar canvas y scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Variables para los campos de dirección
        self.estado_var = tk.StringVar()
        self.municipio_var = tk.StringVar()
        self.parroquia_var = tk.StringVar()
        
        # Diccionario para almacenar las entradas
        self.entradas = {}
        
        # Crear campos
        self.crear_campos()
        
        # Frame para botones (al final de la ventana)
        self.botones_frame = ttk.Frame(self.main_frame, padding="10")
        self.botones_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        
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
        # Frame contenedor para primera fila (datos personales y dirección)
        top_container = ttk.Frame(self.scrollable_frame)
        top_container.pack(fill=tk.X, padx=5, pady=5)
            
        # Frame para datos personales
        datos_frame = ttk.LabelFrame(top_container, text="Datos Personales", padding=10)
        datos_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))

        campos_personales = [
            ("Nombre:", "nombre", "readonly"),
            ("Apellido:", "apellido", "readonly"),
            ("Cédula:", "cedula", "readonly"),
            ("Teléfono:", "telefono", "editable"),
            ("Fecha de Nacimiento:", "fecha_nacimiento", "date_readonly"),
            ("Cargo:", "cargo", "editable"),
            ("Salario:", "salario", "editable"),
            ("Fecha de Contratación:", "fecha_contratacion", "date_readonly"),
            ("Status:", "status", "readonly")
        ]

        for i, (label, key, tipo) in enumerate(campos_personales):
            ttk.Label(datos_frame, text=label).grid(row=i, column=0, sticky='e', padx=5, pady=5)
            
            if tipo.startswith("date"):
                widget = DateEntry(datos_frame, width=20, state='disabled')
            else:
                widget = ttk.Entry(datos_frame, width=30, state='disabled')
                
            widget.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
            self.entradas[key] = widget

        ttk.Label(datos_frame, text="Teléfono:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        telefono_frame = ttk.Frame(datos_frame)
        telefono_frame.grid(row=3, column=1, sticky='w', padx=5, pady=5)
        
        self.prefijo_var = tk.StringVar(value="0424")
        self.prefijo_combo = ttk.Combobox(telefono_frame, 
                                        textvariable=self.prefijo_var,
                                        values=["0414", "0424", "0412", "0416", "0426"], 
                                        width=5, 
                                        state="disabled")
        self.prefijo_combo.pack(side=tk.LEFT, padx=(0,5))
        self.telefono_entry = ttk.Entry(telefono_frame, width=20, state="disabled")
        self.telefono_entry.pack(side=tk.LEFT)
        self.entradas["telefono"] = self.telefono_entry
        self.entradas["prefijo"] = self.prefijo_combo
        self.telefono_entry.bind('<KeyRelease>', self.limit_phone)

        # Frame para dirección (al lado de datos personales)
        direccion_frame = ttk.LabelFrame(top_container, text="Dirección", padding=10)
        direccion_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5,0))

        # Estado
        ttk.Label(direccion_frame, text="Estado:", width=12).grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.estado_combo = ttk.Combobox(direccion_frame, textvariable=self.estado_var,
                                    state="disabled", width=25)
        self.estado_combo.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        # Municipio
        ttk.Label(direccion_frame, text="Municipio:", width=12).grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.municipio_combo = ttk.Combobox(direccion_frame, textvariable=self.municipio_var,
                                        state="disabled", width=25)
        self.municipio_combo.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        # Parroquia
        ttk.Label(direccion_frame, text="Parroquia:", width=12).grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.parroquia_combo = ttk.Combobox(direccion_frame, textvariable=self.parroquia_var,
                                        state="disabled", width=25)
        self.parroquia_combo.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        
        # Calle/Avenida
        ttk.Label(direccion_frame, text="Calle/Av.:", width=12).grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.calle_entry = ttk.Entry(direccion_frame, width=28, state='disabled')
        self.calle_entry.grid(row=3, column=1, sticky='w', padx=5, pady=5)
        
        # Número/Casa
        ttk.Label(direccion_frame, text="N°/Casa:", width=12).grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.numero_entry = ttk.Entry(direccion_frame, width=28, state='disabled')
        self.numero_entry.grid(row=4, column=1, sticky='w', padx=5, pady=5)
        
        # Referencia
        ttk.Label(direccion_frame, text="Referencia:", width=12).grid(row=5, column=0, sticky='e', padx=5, pady=5)
        self.referencia_entry = ttk.Entry(direccion_frame, width=28, state='disabled')
        self.referencia_entry.grid(row=5, column=1, sticky='w', padx=5, pady=5)

        # Frame para dispositivos NFC (debajo de datos y dirección)
        nfc_frame = ttk.LabelFrame(self.scrollable_frame, text="Dispositivos NFC", padding="5")
        nfc_frame.pack(fill=tk.X, padx=5, pady=5)
        
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
        ttk.Button(nfc_buttons_frame, text="Remover Dispositivo",
                command=self.remover_dispositivo).pack(side=tk.LEFT, padx=5)

        # Bindings para actualizar comboboxes
        self.estado_combo.bind('<<ComboboxSelected>>', self.actualizar_municipios)
        self.municipio_combo.bind('<<ComboboxSelected>>', self.actualizar_parroquias)

    def limit_phone(self, event=None):
        value = self.telefono_entry.get()
        if len(value) > 7:
            self.telefono_entry.delete(7, tk.END)

    def actualizar_municipios(self, event=None):
        """Actualizar lista de municipios según el estado seleccionado"""
        try:
            estado = self.estado_var.get()
            if not estado:
                return
                
            query = """
            SELECT m.municipio 
            FROM municipios m 
            JOIN estados e ON m.id_estado = e.id_estado 
            WHERE e.estado = %s 
            ORDER BY m.municipio
            """
            
            municipios = self.db_manager.ejecutar_query(query, (estado,))
            
            if municipios:
                self.municipio_combo['values'] = [m[0] for m in municipios]
            
        except Exception as e:
            print(f"Error al actualizar municipios: {str(e)}")
            messagebox.showerror("Error", f"Error al cargar municipios: {str(e)}")

    def actualizar_parroquias(self, event=None):
        """Actualizar lista de parroquias según el municipio seleccionado"""
        try:
            municipio = self.municipio_var.get()
            if not municipio:
                return
                
            query = """
            SELECT p.parroquia 
            FROM parroquias p 
            JOIN municipios m ON p.id_municipio = m.id_municipio 
            WHERE m.municipio = %s 
            ORDER BY p.parroquia
            """
            
            parroquias = self.db_manager.ejecutar_query(query, (municipio,))
            
            if parroquias:
                self.parroquia_combo['values'] = [p[0] for p in parroquias]
                
        except Exception as e:
            print(f"Error al actualizar parroquias: {str(e)}")
            messagebox.showerror("Error", f"Error al cargar parroquias: {str(e)}")

    def cargar_estados(self):
        """Cargar la lista de estados en el combobox"""
        try:
            query = """
            SELECT estado 
            FROM estados 
            ORDER BY estado
            """
            estados = self.db_manager.ejecutar_query(query)
            
            if estados:
                self.estado_combo['values'] = [estado[0] for estado in estados]
                
        except Exception as e:
            print(f"Error al cargar estados: {str(e)}")
            messagebox.showerror("Error", f"Error al cargar estados: {str(e)}")

    def obtener_direccion_completa(self):
        """Obtener la dirección completa formateada"""
        estado = self.estado_var.get()
        municipio = self.municipio_var.get()
        parroquia = self.parroquia_var.get()
        calle = self.calle_entry.get().strip()
        numero = self.numero_entry.get().strip()
        referencia = self.referencia_entry.get().strip()

        direccion_partes = []
        if calle:
            direccion_partes.append(f"Calle/Av. {calle}")
        if numero:
            direccion_partes.append(f"N°/Casa {numero}")
        if parroquia:
            direccion_partes.append(f"Parroquia {parroquia}")
        if municipio:
            direccion_partes.append(f"Municipio {municipio}")
        if estado:
            direccion_partes.append(f"Estado {estado}")
        if referencia:
            direccion_partes.append(f"(Ref: {referencia})")

        return ", ".join(filter(None, direccion_partes))

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

                # Teléfono
                if empleado.get('telefono'):
                    prefijo = empleado['telefono'][:4]
                    numero = empleado['telefono'][4:]
                    self.prefijo_combo.configure(state='normal')
                    self.prefijo_var.set(prefijo)
                    self.prefijo_combo.configure(state='disabled')
                    self.telefono_entry.configure(state='normal')
                    self.telefono_entry.delete(0, tk.END)
                    self.telefono_entry.insert(0, numero)
                    self.telefono_entry.configure(state='disabled')
                else:
                    self.prefijo_combo.configure(state='disabled')
                    self.telefono_entry.configure(state='disabled')
                
                # Dirección
                if empleado['direccion']:
                    # Cargar estados y habilitar comboboxes temporalmente
                    self.cargar_estados()
                    
                    # Parsear dirección completa
                    direccion = empleado['direccion']
                    partes = direccion.split(", ")
                    
                    for parte in partes:
                        if "Estado" in parte:
                            estado = parte.replace("Estado ", "")
                            self.estado_var.set(estado)
                            self.actualizar_municipios()
                        elif "Municipio" in parte:
                            self.municipio_var.set(parte.replace("Municipio ", ""))
                            self.actualizar_parroquias()
                        elif "Parroquia" in parte:
                            self.parroquia_var.set(parte.replace("Parroquia ", ""))
                        elif "Calle/Av." in parte:
                            self.calle_entry.configure(state='normal')
                            self.calle_entry.delete(0, tk.END)
                            self.calle_entry.insert(0, parte.replace("Calle/Av. ", ""))
                            self.calle_entry.configure(state='disabled')
                        elif "N°/Casa" in parte:
                            self.numero_entry.configure(state='normal')
                            self.numero_entry.delete(0, tk.END)
                            self.numero_entry.insert(0, parte.replace("N°/Casa ", ""))
                            self.numero_entry.configure(state='disabled')
                        elif "Ref:" in parte:
                            self.referencia_entry.configure(state='normal')
                            self.referencia_entry.delete(0, tk.END)
                            self.referencia_entry.insert(0, parte.replace("(Ref: ", "").replace(")", ""))
                            self.referencia_entry.configure(state='disabled')
                
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

    def activar_edicion(self):
        """Activar la edición de campos permitidos"""
        campos_no_editables = ["nombre", "apellido", "cedula", "fecha_nacimiento", 
                            "fecha_contratacion", "status"]
        
        # Activar comboboxes de dirección y prefijo
        self.estado_combo.config(state='readonly')
        self.municipio_combo.config(state='readonly')
        self.parroquia_combo.config(state='readonly')
        self.prefijo_combo.config(state='readonly')
        self.calle_entry.config(state='normal')
        self.numero_entry.config(state='normal')
        self.referencia_entry.config(state='normal')
        
        # Guardar valor actual del cargo antes de destruir el widget
        cargo_actual = self.entradas["cargo"].get()
        
        # Configurar el campo de cargo
        parent = self.entradas["cargo"].master
        grid_info = self.entradas["cargo"].grid_info()
        self.entradas["cargo"].destroy()
        
        self.combo_cargo = ttk.Combobox(
            parent,
            values=["Gerente", "Supervisor", "Analista", "Empleado"],
            state="readonly",
            width=30
        )
        self.combo_cargo.set(cargo_actual)
        self.combo_cargo.grid(row=grid_info['row'], column=grid_info['column'], 
                        sticky=grid_info['sticky'], padx=grid_info['padx'], 
                        pady=grid_info['pady'])
        self.entradas["cargo"] = self.combo_cargo
        
        # Activar campos editables
        for key, widget in self.entradas.items():
            if key not in campos_no_editables and key != "cargo":
                widget.config(state='normal')
        
        # Configurar estado de botones
        self.btn_editar.config(state='disabled')
        self.btn_guardar.config(state='normal')
        self.btn_cancelar.config(state='normal')
        
    def desactivar_edicion(self):
        # Desactivar comboboxes
        self.estado_combo.config(state='disabled')
        self.municipio_combo.config(state='disabled')
        self.parroquia_combo.config(state='disabled')
        self.calle_entry.config(state='disabled')
        self.numero_entry.config(state='disabled')
        self.referencia_entry.config(state='disabled')
        self.prefijo_combo.config(state='disabled')
        
        # Restaurar cargo a Entry
        if hasattr(self, 'combo_cargo'):
            cargo_actual = self.combo_cargo.get()
            parent = self.combo_cargo.master
            grid_info = self.combo_cargo.grid_info()
            cargo_entry = ttk.Entry(parent, width=30)
            cargo_entry.grid(row=grid_info['row'], 
                            column=grid_info['column'],
                            sticky=grid_info['sticky'],
                            padx=grid_info['padx'],
                            pady=grid_info['pady'])
            cargo_entry.insert(0, cargo_actual)
            cargo_entry.config(state='disabled')
            
            self.combo_cargo.destroy()
            self.entradas["cargo"] = cargo_entry
        
        # Desactivar campos
        for widget in self.entradas.values():
            widget.config(state='disabled')
        
        # Actualizar botones
        self.btn_editar.config(state='normal')
        self.btn_guardar.config(state='disabled')
        self.btn_cancelar.config(state='disabled')
    
    def validar_telefono(self, numero):
        """Validar formato del número de teléfono"""
        if not numero:
            return True
                
        # Eliminar espacios
        numero = numero.strip()
        
        # Verificar que solo contenga números
        if not numero.isdigit():
            raise ValueError("El número de teléfono solo debe contener dígitos")
        
        # Verificar longitud (7 dígitos después del prefijo)
        if len(numero) != 7:
            raise ValueError("El número de teléfono debe tener 7 dígitos (sin contar el prefijo)")
                
        return True
    
    def guardar_cambios(self):
        try:
            # Validar teléfono
            numero_telefono = self.telefono_entry.get().strip()
            if numero_telefono:
                try:
                    self.validar_telefono(numero_telefono)
                    telefono_completo = f"{self.prefijo_var.get()}{numero_telefono}"
                except ValueError as e:
                    messagebox.showerror("Error", str(e))
                    return
            
            # Recopilar datos
            datos = {
            'nombre': self.entradas["nombre"].get().strip(),
            'apellido': self.entradas["apellido"].get().strip(),
            'cargo': self.entradas["cargo"].get().strip(),
            'salario': float(self.entradas["salario"].get().replace(',', '')),
            'telefono': telefono_completo if numero_telefono else None,
            'direccion': self.obtener_direccion_completa(),
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
    
    def agregar_tarjeta(self):
        """Agregar una nueva tarjeta NFC al empleado"""
        dialog = tk.Toplevel(self)
        dialog.title("Agregar Tarjeta NFC")
        dialog.geometry("400x200")
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
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
                self.cargar_datos()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error al asignar tarjeta: {str(e)}")
        
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
                self.cargar_datos()
            except Exception as e:
                messagebox.showerror("Error", f"Error al remover dispositivo: {str(e)}")

class EmpleadosForm(ttk.Frame):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        
        self.pack(fill=tk.BOTH, expand=True)
        
        # Frame principal
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame superior con título, búsqueda y botón de nuevo empleado
        self.crear_frame_superior()
        
        # Frame para el Treeview
        self.crear_frame_lista()
        
        # Frame para botones de acción
        self.crear_frame_acciones()
        
        # Cargar datos iniciales
        self.cargar_empleados()
        
        # Bindings
        self.tree.bind('<Double-1>', lambda e: self.ver_detalles())
        self.search_var.trace('w', lambda *args: self.filtrar_empleados())

    def crear_frame_superior(self):
        """Crear frame superior con título, búsqueda y botón nuevo"""
        top_frame = ttk.Frame(self.main_frame)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Título
        ttk.Label(top_frame, text="Lista de Empleados", 
                 font=('Helvetica', 12, 'bold')).pack(side=tk.LEFT, pady=5)
        
        # Botón Nuevo Empleado
        ttk.Button(top_frame, text="Nuevo Empleado",
                  command=self.abrir_registro).pack(side=tk.RIGHT, padx=5)
        
        # Frame de búsqueda
        search_frame = ttk.LabelFrame(top_frame, text="Búsqueda", padding=5)
        search_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Label(search_frame, text="🔍").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, 
                                    textvariable=self.search_var,
                                    width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)

    def crear_frame_lista(self):
        """Crear frame con el Treeview de empleados"""
        # Crear Treeview con ID oculto
        self.tree = ttk.Treeview(self.main_frame, columns=(
            "ID", "Nombre", "Apellido", "Cedula", "Cargo", "Salario", 
            "Fecha_Contratacion", "Status"), 
            show='headings', displaycolumns=(
            "Nombre", "Apellido", "Cedula", "Cargo", "Salario", 
            "Fecha_Contratacion", "Status"))
        
        # Configurar columnas
        self.tree.column("ID", width=0, stretch=False)
        self.tree.column("Nombre", width=150)
        self.tree.column("Apellido", width=150)
        self.tree.column("Cedula", width=100)
        self.tree.column("Cargo", width=120)
        self.tree.column("Salario", width=100)
        self.tree.column("Fecha_Contratacion", width=120)
        self.tree.column("Status", width=80)
        
        # Configurar encabezados
        for col in self.tree['columns']:
            self.tree.heading(col, text=col.replace('_', ' '))
        
        # Scrollbars
        vsb = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.main_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Configurar tags para estados
        self.tree.tag_configure('inactivo', foreground='gray')

    def crear_frame_acciones(self):
        """Crear frame con botones de acción"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Ver Detalles", 
                  command=self.ver_detalles).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cambiar Status",
                  command=self.cambiar_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar Lista",
                  command=self.cargar_empleados).pack(side=tk.LEFT, padx=5)

    def abrir_registro(self):
        """Abrir formulario de registro de nuevo empleado"""
        registro_form = RegistroEmpleadoForm(self, self.db_manager)
        self.wait_window(registro_form)

    def ver_detalles(self):
        """Abrir formulario de detalles del empleado seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un empleado")
            return
            
        item = self.tree.item(selected[0])
        id_empleado = item['values'][0]
        print(f"ID del empleado seleccionado {id_empleado}")

        detalles_form = EmpleadoDetallesForm(self, self.db_manager, id_empleado)

        # Centrar la ventana
        detalles_form.update_idletasks()
        width = detalles_form.winfo_width()
        height = detalles_form.winfo_height()
        x = (detalles_form.winfo_screenwidth() // 2) - (width // 2)
        y = (detalles_form.winfo_screenheight() // 2) - (height // 2)
        detalles_form.geometry(f'+{x}+{y}')

        detalles_form.grab_set()

    def cambiar_status(self):
        """Cambiar el status del empleado seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un empleado")
            return
            
        item = self.tree.item(selected[0])
        id_empleado = item['values'][0]  # ID es la primera columna
        nombre_empleado = f"{item['values'][1]} {item['values'][2]}"  # Nombre y Apellido
        status_actual = item['values'][7] if len(item['values']) > 7 else 'activo'
        
        # Crear ventana de diálogo para el cambio de status
        dialog = tk.Toplevel(self)
        dialog.title("Cambiar Status de Empleado")
        dialog.geometry("400x400")
        dialog.grab_set()  # Hacer la ventana modal
        
        # Frame principal
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Información del empleado
        ttk.Label(main_frame, text=f"Empleado: {nombre_empleado}").pack(fill=tk.X, pady=5)
        ttk.Label(main_frame, text=f"Status actual: {status_actual}").pack(fill=tk.X, pady=5)
        
        # Nuevo status
        ttk.Label(main_frame, text="Nuevo status:").pack(fill=tk.X, pady=5)
        nuevo_status = tk.StringVar(value='activo' if status_actual == 'inactivo' else 'inactivo')
        status_combo = ttk.Combobox(main_frame, 
                                textvariable=nuevo_status,
                                values=['activo', 'inactivo'],
                                state='readonly')
        status_combo.pack(fill=tk.X, pady=5)
        
        # Tipo de motivo
        ttk.Label(main_frame, text="Tipo de motivo:").pack(fill=tk.X, pady=5)
        tipo_motivo = tk.StringVar(value="Otros")
        motivos = ["Vacaciones", "Permiso Laboral", "Licencia Médica", "Otros"]
        motivo_combo = ttk.Combobox(main_frame, 
                                textvariable=tipo_motivo,
                                values=motivos,
                                state='readonly')
        motivo_combo.pack(fill=tk.X, pady=5)
        
        # Descripción del motivo
        ttk.Label(main_frame, text="Descripción:").pack(fill=tk.X, pady=5)
        motivo_text = tk.Text(main_frame, height=4, width=40)
        motivo_text.pack(fill=tk.X, pady=5)
        
        def confirmar_cambio():
            if not motivo_text.get("1.0", tk.END).strip():
                messagebox.showwarning("Advertencia", 
                                    "Por favor ingrese una descripción del motivo")
                return
                
            try:
                motivo_completo = f"{tipo_motivo.get()}: {motivo_text.get('1.0', tk.END).strip()}"
                self.db_manager.cambiar_status_empleado(
                    id_empleado,
                    nuevo_status.get(),
                    motivo_completo
                )
                messagebox.showinfo("Éxito", 
                                f"Status del empleado actualizado a {nuevo_status.get()}")
                dialog.destroy()
                self.cargar_empleados()  # Actualizar la lista
            except Exception as e:
                messagebox.showerror("Error", f"Error al cambiar el status: {str(e)}")
        
        # Frame para botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="Confirmar",
                command=confirmar_cambio).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar",
                command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def cargar_empleados(self):
        """Cargar la lista de empleados"""
        # Limpiar Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            empleados = self.db_manager.ver_empleados()
            for emp in empleados:
                valores = list(emp)
                # Formatear salario
                valores[5] = f"{float(valores[5]):,.2f}"
                
                # Agregar estado si no existe
                status = valores[7] if len(valores) > 7 else 'activo'
                if len(valores) <= 7:
                    valores.append(status)
                
                self.tree.insert('', 'end', values=valores, tags=(status.lower(),))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar empleados: {str(e)}")

    def filtrar_empleados(self):
        """Filtrar empleados según el texto de búsqueda"""
        texto = self.search_var.get().lower()
        
        # Limpiar Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            empleados = self.db_manager.ver_empleados()
            for emp in empleados:
                # Verificar si el texto de búsqueda está en algún campo
                if any(str(valor).lower().find(texto) >= 0 for valor in emp):
                    valores = list(emp)
                    valores[5] = f"{float(valores[5]):,.2f}"
                    status = valores[7] if len(valores) > 7 else 'activo'
                    if len(valores) <= 7:
                        valores.append(status)
                    self.tree.insert('', 'end', values=valores, tags=(status.lower(),))
        except Exception as e:
            messagebox.showerror("Error", f"Error al filtrar empleados: {str(e)}")