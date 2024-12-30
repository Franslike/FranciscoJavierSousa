import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import traceback
import bcrypt

class RegistroEmpleadoForm(tk.Toplevel):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.parent = parent
        self.db_manager = db_manager
        
        self.title("Registro de Empleado")
        self.geometry("800x700")
        
        # Diccionario para salarios base por cargo
        self.SALARIOS_BASE = {
            "Gerente": 18000.00,
            "Supervisor": 15000.00,
            "Analista": 15000.00,
            "Empleado": 12000.00
        }
        
        # Frame principal con scroll
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas y scrollbar
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
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
        
        # Inicializar variables
        self.estado_var = tk.StringVar()
        self.municipio_var = tk.StringVar()
        self.parroquia_var = tk.StringVar()
        self.cargo_var = tk.StringVar()
        self.uid_nfc_var = tk.StringVar()
        self.nacionalidad_var = tk.StringVar(value="V")
        self.prefijo_var = tk.StringVar(value="0424")
        
        # Crear el formulario
        self.crear_formulario()
        
        # Bindings para actualizar comboboxes
        self.estado_combo.bind('<<ComboboxSelected>>', self.actualizar_municipios)
        self.municipio_combo.bind('<<ComboboxSelected>>', self.actualizar_parroquias)
        self.cargo_combo.bind('<<ComboboxSelected>>', self.actualizar_salario)
        
        # Cargar datos iniciales
        self.cargar_estados()
        self.cargar_uids_disponibles()
        
        # Centrar la ventana
        self.center_window()
        
        # Hacer que la ventana sea modal
        self.transient(parent)
        self.grab_set()

    def crear_formulario(self):
        # Frame contenedor para primera fila (datos personales y dirección)
        top_container = ttk.Frame(self.scrollable_frame)
        top_container.pack(fill=tk.X, padx=5, pady=5)
        
        # Frame para datos personales
        datos_frame = ttk.LabelFrame(top_container, text="Datos Personales", padding=10)
        datos_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
        
        # Campos de datos personales
        ttk.Label(datos_frame, text="Nombre:", width=15).grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.nombre_entry = ttk.Entry(datos_frame, width=25)
        self.nombre_entry.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Label(datos_frame, text="Apellido:", width=15).grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.apellido_entry = ttk.Entry(datos_frame, width=25)
        self.apellido_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        # Cédula con selector de nacionalidad
        ttk.Label(datos_frame, text="Cédula:", width=15).grid(row=2, column=0, sticky='e', padx=5, pady=5)
        cedula_frame = ttk.Frame(datos_frame)
        cedula_frame.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        
        self.nacionalidad_combo = ttk.Combobox(cedula_frame, 
                                            textvariable=self.nacionalidad_var,
                                            values=["V", "E"], 
                                            width=3, 
                                            state="readonly")
        self.nacionalidad_combo.pack(side=tk.LEFT, padx=(0,5))
        self.cedula_entry = ttk.Entry(cedula_frame, width=20)
        self.cedula_entry.pack(side=tk.LEFT)
        
        # Teléfono con selector de prefijo
        ttk.Label(datos_frame, text="Teléfono:", width=15).grid(row=3, column=0, sticky='e', padx=5, pady=5)
        telefono_frame = ttk.Frame(datos_frame)
        telefono_frame.grid(row=3, column=1, sticky='w', padx=5, pady=5)
        
        self.prefijo_combo = ttk.Combobox(telefono_frame, 
                                        textvariable=self.prefijo_var,
                                        values=["0414", "0424", "0412", "0416", "0426"], 
                                        width=5, 
                                        state="readonly")
        self.prefijo_combo.pack(side=tk.LEFT, padx=(0,5))
        self.telefono_entry = ttk.Entry(telefono_frame, width=18)
        self.telefono_entry.pack(side=tk.LEFT)
        self.telefono_entry.bind('<KeyRelease>', self.limit_phone)
        
        # Fecha de nacimiento
        ttk.Label(datos_frame, text="Fecha Nac.:", width=15).grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.fecha_nacimiento = DateEntry(
            datos_frame, 
            width=12,
            date_pattern='dd/mm/yyyy',  # Forzar formato de 4 dígitos
            year_range=range(1950, datetime.now().year + 1),  # Rango razonable de años
            showweeknumbers=False,
            background='darkblue',
            foreground='white',
            borderwidth=2
        )
        self.fecha_nacimiento.grid(row=4, column=1, sticky='w', padx=5, pady=5)
        
        # Frame para dirección
        direccion_frame = ttk.LabelFrame(top_container, text="Dirección", padding=10)
        direccion_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5,0))
        
        # Estado
        ttk.Label(direccion_frame, text="Estado:", width=12).grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.estado_combo = ttk.Combobox(direccion_frame, textvariable=self.estado_var,
                                       state="readonly", width=25)
        self.estado_combo.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        # Municipio
        ttk.Label(direccion_frame, text="Municipio:", width=12).grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.municipio_combo = ttk.Combobox(direccion_frame, textvariable=self.municipio_var,
                                          state="readonly", width=25)
        self.municipio_combo.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        # Parroquia
        ttk.Label(direccion_frame, text="Parroquia:", width=12).grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.parroquia_combo = ttk.Combobox(direccion_frame, textvariable=self.parroquia_var,
                                          state="readonly", width=25)
        self.parroquia_combo.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        
        # Calle/Avenida
        ttk.Label(direccion_frame, text="Calle/Av.:", width=12).grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.calle_entry = ttk.Entry(direccion_frame, width=28)
        self.calle_entry.grid(row=3, column=1, sticky='w', padx=5, pady=5)
        
        # Número/Casa
        ttk.Label(direccion_frame, text="N°/Casa:", width=12).grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.numero_entry = ttk.Entry(direccion_frame, width=28)
        self.numero_entry.grid(row=4, column=1, sticky='w', padx=5, pady=5)
        
        # Referencia
        ttk.Label(direccion_frame, text="Referencia:", width=12).grid(row=5, column=0, sticky='e', padx=5, pady=5)
        self.referencia_entry = ttk.Entry(direccion_frame, width=28)
        self.referencia_entry.grid(row=5, column=1, sticky='w', padx=5, pady=5)

        # Frame para datos laborales
        laboral_frame = ttk.LabelFrame(self.scrollable_frame, text="Datos Laborales", padding=10)
        laboral_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Grid para datos laborales
        ttk.Label(laboral_frame, text="Cargo:", width=15).grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.cargo_var = tk.StringVar()
        self.cargo_combo = ttk.Combobox(laboral_frame, textvariable=self.cargo_var,
                                    values=list(self.SALARIOS_BASE.keys()), state="readonly", width=25)
        self.cargo_combo.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Label(laboral_frame, text="Salario:", width=15).grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.salario_entry = ttk.Entry(laboral_frame, width=28)
        self.salario_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Label(laboral_frame, text="Fecha Contratación:", width=15).grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.fecha_contratacion = DateEntry(laboral_frame, width=20)
        self.fecha_contratacion.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        
        # Tarjeta NFC (ahora dentro de datos laborales)
        ttk.Label(laboral_frame, text="Tarjeta NFC:", width=15).grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.uid_nfc_var = tk.StringVar()
        self.uid_nfc_combo = ttk.Combobox(laboral_frame, textvariable=self.uid_nfc_var,
                                        state="readonly", width=25)
        self.uid_nfc_combo.grid(row=3, column=1, sticky='w', padx=5, pady=5)
        
        # Frame para permisos
        permisos_frame = ttk.LabelFrame(self.scrollable_frame, text="Permisos de Usuario", padding=10)
        permisos_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Grid para permisos
        self.permisos_vars = {}
        permisos = self.db_manager.obtener_permisos_sistema()
        
        for i, permiso in enumerate(permisos):
            var = tk.BooleanVar()
            self.permisos_vars[permiso['codigo']] = var
            ttk.Checkbutton(permisos_frame, 
                        text=permiso['descripcion'],
                        variable=var).grid(row=i//3, column=i%3, padx=10, pady=2, sticky='w')
        
        # Frame para botones
        botones_frame = ttk.Frame(self.scrollable_frame)
        botones_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(botones_frame, text="Guardar", 
                command=self.guardar_empleado).pack(side=tk.LEFT, padx=5)
        ttk.Button(botones_frame, text="Cancelar",
                command=self.destroy).pack(side=tk.LEFT, padx=5)
        
    def limit_phone(self, event=None):
        value = self.telefono_entry.get()
        if len(value) > 7:
            self.telefono_entry.delete(7, tk.END)

    def cargar_uids_disponibles(self):
        """Cargar los UIDs NFC disponibles"""
        uids = self.db_manager.obtener_uids_disponibles()
        if uids:
            self.uid_nfc_combo['values'] = [f"{uid[0]} - {uid[1]}" for uid in uids]
        else:
            self.uid_nfc_combo['values'] = ["No hay tarjetas disponibles"]

    def actualizar_salario(self, event=None):
        """Actualizar el salario base según el cargo seleccionado"""
        cargo_seleccionado = self.cargo_var.get()
        if cargo_seleccionado in self.SALARIOS_BASE:
            salario_base = self.SALARIOS_BASE[cargo_seleccionado]
            self.salario_entry.delete(0, tk.END)
            self.salario_entry.insert(0, f"{salario_base:.2f}")

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
                valores_estado = [estado[0] for estado in estados]
                self.estado_combo['values'] = valores_estado
                print(f"Estados cargados: {valores_estado}")  # Debug
            else:
                print("No se encontraron estados en la base de datos")
                
        except Exception as e:
            print(f"Error al cargar estados: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al cargar estados: {str(e)}")

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
                print(f"Municipios cargados para {estado}: {[m[0] for m in municipios]}")  # Debug
            else:
                print(f"No se encontraron municipios para el estado {estado}")
                
        except Exception as e:
            print(f"Error al actualizar municipios: {str(e)}")
            traceback.print_exc()
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
                print(f"Parroquias cargadas para {municipio}: {[p[0] for p in parroquias]}")  # Debug
            else:
                print(f"No se encontraron parroquias para el municipio {municipio}")
                
        except Exception as e:
            print(f"Error al actualizar parroquias: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al cargar parroquias: {str(e)}")

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
    
    def validar_telefono(self, numero):
        """Validar que el número de teléfono tenga el formato correcto"""
        # Eliminar espacios en blanco
        numero = numero.strip()
        
        # Verificar que solo contenga números
        if not numero.isdigit():
            raise ValueError("El número de teléfono solo debe contener dígitos")
        
        # Verificar la longitud
        if len(numero) != 7:
            raise ValueError("El número de teléfono debe tener exactamente 7 dígitos")
            
        return True
    
    def validar_fecha_nacimiento(self, fecha):
        """Validar que la fecha de nacimiento sea razonable"""
        hoy = datetime.now().date()
        edad = hoy.year - fecha.year - ((hoy.month, hoy.day) < (fecha.month, fecha.day))
        
        if edad < 18:
            raise ValueError("El empleado debe ser mayor de 18 años")
        if edad > 100:
            raise ValueError("La fecha de nacimiento parece incorrecta")
        
        return True

    def guardar_empleado(self):
        """Guardar el nuevo empleado"""
        try:
            # Validar edad mínima
            fecha_nacimiento = self.fecha_nacimiento.get_date()
            self.validar_fecha_nacimiento(fecha_nacimiento)
                
            # Validar teléfono
            numero_telefono = self.telefono_entry.get()
            try:
                self.validar_telefono(numero_telefono)
                telefono_completo = f"{self.prefijo_var.get()}{numero_telefono}"
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                self.telefono_entry.focus()
                return
                
            # Validar campos de dirección
            if not all([
                self.estado_var.get(),
                self.municipio_var.get(),
                self.parroquia_var.get(),
                self.calle_entry.get().strip()
            ]):
                messagebox.showwarning(
                    "Advertencia", 
                    "Por favor complete los campos obligatorios de la dirección"
                )
                return

            # Obtener todos los valores
            datos = {
                'nombre': self.nombre_entry.get().strip(),
                'apellido': self.apellido_entry.get().strip(),
                'cedula': self.nacionalidad_var.get() + self.cedula_entry.get().strip(),
                'telefono': telefono_completo,  # Agregamos el teléfono a los datos
                'cargo': self.cargo_var.get(),
                'salario': float(self.salario_entry.get().strip()),
                'fecha_contratacion': self.fecha_contratacion.get_date(),
                'fecha_nacimiento': fecha_nacimiento,
                'uid_tarjeta': self.uid_nfc_var.get().split(' - ')[0] if self.uid_nfc_var.get() else None,
                'permisos': [codigo for codigo, var in self.permisos_vars.items() if var.get()],
                'direccion': self.obtener_direccion_completa()
            }
            
            # Validaciones básicas
            if not all([datos['nombre'], datos['apellido'], datos['cedula'],
                    datos['telefono'], datos['cargo'], datos['salario'] > 0]):
                messagebox.showwarning(
                    "Advertencia", 
                    "Por favor complete todos los campos obligatorios"
                )
                return
                
            # Verificar empleado existente
            if self.db_manager.verificar_empleado_existente(datos['cedula']):
                messagebox.showerror(
                    "Error", 
                    "Ya existe un empleado con esta cédula"
                )
                return
            
            # Validar que la fecha de contratación no sea anterior a que la persona tenga 18 años
            fecha_minima_contratacion = datetime(
                fecha_nacimiento.year + 18,
                fecha_nacimiento.month,
                fecha_nacimiento.day
            ).date()
            
            if datos['fecha_contratacion'] < fecha_minima_contratacion:
                messagebox.showerror(
                    "Error",
                    "La fecha de contratación no puede ser anterior a que el empleado tenga 18 años."
                )
                return
            
            # Registrar empleado
            self.db_manager.registrar_empleado_con_nfc(**datos)
            
            messagebox.showinfo(
                "Éxito",
                f"Empleado registrado correctamente.\n" +
                f"Usuario: {datos['cedula']}\n" +
                "Contraseña inicial: La misma cédula"
            )
            
            # Actualizar lista de empleados en el formulario padre
            if hasattr(self.parent, 'cargar_empleados'):
                self.parent.cargar_empleados()
                
            self.destroy()
            
        except ValueError as e:
            if "fecha" in str(e).lower():
                messagebox.showerror(
                    "Error", 
                    "Por favor verifique las fechas ingresadas"
                )
            else:
                messagebox.showerror(
                    "Error", 
                    "Por favor verifique los valores ingresados"
                )
        except Exception as e:
            messagebox.showerror(
                "Error", 
                f"Error al registrar empleado: {str(e)}"
            )
            
    def center_window(self):
        """Centrar la ventana en la pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')