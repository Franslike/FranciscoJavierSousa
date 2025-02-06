import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
from decimal import Decimal
from util.ayuda import Ayuda

class PrestamoNuevoForm(tk.Toplevel):
    def __init__(self, parent, db_manager, id_empleado):
        super().__init__(parent)
        self.parent = parent
        self.db_manager = db_manager
        self.id_empleado = id_empleado
        
        self.title("Solicitar Préstamo")
        self.geometry("360x520")
        self.configure(bg='white')

        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título y subtítulo
        ttk.Label(main_frame, 
                 text="Solicitar Préstamo",
                 font=('Arial', 16, 'bold'),
                 foreground='#2596be').pack(anchor='center')

        ttk.Label(main_frame,
                 text="Complete los datos para solicitar su préstamo",
                 font=('Arial', 10),
                 foreground='#666666').pack(pady=(5,15))

        # Frame para datos del préstamo
        campos_frame = ttk.LabelFrame(main_frame, text="Datos del Préstamo", padding=10)
        campos_frame.pack(fill=tk.X, pady=5)

        ttk.Label(campos_frame, text="Monto solicitado:").pack(pady=5)
        self.monto_entry = ttk.Entry(campos_frame, width=50)
        self.monto_entry.pack(pady=5)

        ttk.Label(campos_frame, text="Número de cuotas:").pack(pady=5)
        self.cuotas_entry = ttk.Entry(campos_frame, width=50)
        self.cuotas_entry.pack(pady=5)

        self.cuota_label = ttk.Label(campos_frame, text="Cuota quincenal: Bs. 0,00")
        self.cuota_label.pack(pady=10)

        # Frame para motivo
        motivo_frame = ttk.LabelFrame(main_frame, text="Motivo del Préstamo", padding=10)
        motivo_frame.pack(fill=tk.X, pady=5)
        
        self.motivo_text = tk.Text(motivo_frame, height=4, width=40)
        self.motivo_text.pack(pady=5)

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)

        self.solicitar_btn = tk.Button(
            button_frame,
            text="Solicitar",
            font=("Arial", 10, "bold"),
            fg="#ffffff",
            bg="#0D6EFD",
            activebackground="#0B5ED7",
            relief="flat",
            cursor="hand2",
            width=15,
            command=self.solicitar_prestamo
        )
        self.solicitar_btn.pack(side=tk.LEFT, padx=5)

        self.cancelar_btn = tk.Button(
            button_frame,
            text="Cancelar", 
            font=("Arial", 10, "bold"),
            fg="#ffffff",
            bg="#6C757D",
            activebackground="#5C636A",
            relief="flat",
            cursor="hand2",
            width=15,
            command=self.destroy
        )
        self.cancelar_btn.pack(side=tk.LEFT, padx=5)

        # Eventos hover
        self.solicitar_btn.bind("<Enter>", lambda e: e.widget.config(bg="#0B5ED7"))
        self.solicitar_btn.bind("<Leave>", lambda e: e.widget.config(bg="#0D6EFD"))
        self.cancelar_btn.bind("<Enter>", lambda e: e.widget.config(bg="#5C636A"))
        self.cancelar_btn.bind("<Leave>", lambda e: e.widget.config(bg="#6C757D"))

        # Bindings para cálculo
        self.monto_entry.bind('<KeyRelease>', lambda e: self.calcular_cuota())
        self.cuotas_entry.bind('<KeyRelease>', lambda e: self.calcular_cuota())

        # Centrar la ventana:
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2) 
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def calcular_cuota(self):
        """Calcular cuota quincenal"""
        try:
            monto = Decimal(self.monto_entry.get() or '0')
            cuotas = int(self.cuotas_entry.get() or '0')
            
            if monto > 0 and cuotas > 0:
                cuota = monto / Decimal(str(cuotas))
                self.cuota_label.config(text=f"Cuota quincenal: Bs. {cuota:,.2f}")
            else:
                self.cuota_label.config(text="Cuota quincenal: Bs. 0,00")
        except (ValueError, decimal.InvalidOperation):
            self.cuota_label.config(text="Cuota quincenal: Bs. 0,00")
    
    def solicitar_prestamo(self):
        """Enviar solicitud de préstamo"""
        try:
            monto = Decimal(self.monto_entry.get())
            cuotas = int(self.cuotas_entry.get())
            motivo = self.motivo_text.get("1.0", tk.END).strip()
            
            if monto <= 0:
                messagebox.showerror("Error", "El monto debe ser mayor a cero")
                return
            
            if cuotas <= 0:
                messagebox.showerror("Error", "El número de cuotas debe ser mayor a cero")
                return
            
            if not motivo:
                messagebox.showerror("Error", "Por favor indique el motivo del préstamo")
                return
            
            datos_prestamo = {
                'id_empleado': self.id_empleado,
                'monto_total': monto,
                'cuotas_totales': cuotas,
                'monto_cuota': monto / Decimal(str(cuotas)),
                'motivo': motivo,
                'fecha_solicitud': datetime.now().date()
            }
            
            self.db_manager.registrar_prestamo(datos_prestamo)
            # Registro de auditoria
            detalle = (f"Nueva solicitud de préstamo registrada:\n"
                    f"Empleado: {self.parent.usuario_actual['nombre']} {self.parent.usuario_actual['apellido']}\n"
                    f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Acción realizada desde la interfaz.")
            
            self.db_manager.registrar_auditoria(
                usuario=f"{self.parent.usuario_actual['nombre']} {self.parent.usuario_actual['apellido']}",
                rol=f"{self.usuario_actual['rol']}",
                accion='Nueva solicitud',
                tabla='prestamos',
                detalle=detalle)
            
            messagebox.showinfo("Éxito", "Solicitud enviada correctamente")
            self.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores válidos")

class PrestamosForm(ttk.Frame):
    def __init__(self, parent, db_manager, usuario_actual):
        super().__init__(parent)
        self.db_manager = db_manager
        self.usuario_actual = usuario_actual
        self.sistema_ayuda = Ayuda()

        self.bind_all("<F1>", self.mostrar_ayuda)
        
        self.pack(fill=tk.BOTH, expand=True)

        # Frame principal
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Titulo
        ttk.Label(self.main_frame, text="Préstamos", font=('Helvetica', 12, 'bold')).pack(anchor='w', pady=(0,5))
        
        # Frame superior
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(fill=tk.X, pady=5)
        
        # Verificar si tiene acceso global al módulo de préstamos
        alcance = self.db_manager.verificar_permiso(
            self.usuario_actual['id_usuario'], 
            'prestamos.gestion')
        
        if not alcance:
            messagebox.showerror("Error", "No tienes los permisos suficientes para esta opción.")
            self.destroy()
            return

        self.tiene_acceso_global = alcance == 'GLOBAL'
        self.tiene_acceso_personal = True 

        # La interfaz depende del tipo de acceso
        if self.tiene_acceso_global:
            # Mostrar filtros y controles completos
            ttk.Label(self.top_frame, text="Estado:").pack(side=tk.LEFT, padx=5)
            self.estado_var = tk.StringVar()
            estados = ['Todos', 'Pendiente', 'Aprobado', 'Rechazado', 'Activo', 'Liquidado']
            self.estado_combo = ttk.Combobox(self.top_frame,
                                         textvariable=self.estado_var,
                                         values=estados,
                                         state="readonly")
            self.estado_combo.pack(side=tk.LEFT, padx=5)
            self.estado_combo.set('Todos')
            
            ttk.Label(self.top_frame, text="Buscar:").pack(side=tk.LEFT, padx=5)
            self.search_var = tk.StringVar()
            self.search_entry = ttk.Entry(self.top_frame, textvariable=self.search_var)
            self.search_entry.pack(side=tk.LEFT, padx=5)
        else:
            # Vista limitada - solo sus préstamos
            titulo = ttk.Label(self.top_frame,
                             text="Mis Préstamos",
                             font=('Helvetica', 12, 'bold'))
            titulo.pack(side=tk.LEFT, padx=5)

        # Botón de Nueva Solicitud
        ttk.Button(self.top_frame, text="Nueva Solicitud",
                  command=self.nueva_solicitud).pack(side=tk.RIGHT, padx=5)

        # Frame para el Treeview
        self.tree_frame = ttk.Frame(self.main_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Crear Treeview
        self.tree = ttk.Treeview(self.tree_frame, columns=(
            "id", "empleado", "monto", "cuotas", "monto_cuota", 
            "fecha_solicitud", "estado", "saldo"
        ), show='headings')
        
        # Configurar columnas
        self.tree.heading("id", text="ID")
        self.tree.heading("empleado", text="Empleado")
        self.tree.heading("monto", text="Monto Total")
        self.tree.heading("cuotas", text="Cuotas")
        self.tree.heading("monto_cuota", text="Cuota")
        self.tree.heading("fecha_solicitud", text="Fecha Solicitud")
        self.tree.heading("estado", text="Estado")
        self.tree.heading("saldo", text="Saldo Pendiente")
        
        # Configurar anchos de columna
        self.tree.column("id", width=0, stretch=False)
        self.tree.column("empleado", width=200)
        self.tree.column("monto", width=100)
        self.tree.column("cuotas", width=70)
        self.tree.column("monto_cuota", width=100)
        self.tree.column("fecha_solicitud", width=100)
        self.tree.column("estado", width=100)
        self.tree.column("saldo", width=100)
        
        # Scrollbars
        # scrolly = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        # # scrollx = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        # self.tree.configure(yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)
        
        # Pack Treeview y scrollbars
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        # scrollx.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Frame para botones
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=10)
        
        # Botones según rol y permisos
        if self.tiene_acceso_global:  # Cambiado de verificar_permiso a tiene_acceso_global
            ttk.Button(self.button_frame, text="Aprobar",
                    command=self.aprobar_prestamo).pack(side=tk.LEFT, padx=5)
            ttk.Button(self.button_frame, text="Rechazar",
                    command=self.rechazar_prestamo).pack(side=tk.LEFT, padx=5)

        ttk.Button(self.button_frame, text="Ver Detalles",
                command=self.ver_detalles).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Actualizar",
                command=self.cargar_prestamos).pack(side=tk.LEFT, padx=5)
        
        # Configurar tags para colores según estado
        self.tree.tag_configure('pendiente', background='#fff3cd')
        self.tree.tag_configure('aprobado', background='#d1e7dd')
        self.tree.tag_configure('rechazado', background='#f8d7da')
        self.tree.tag_configure('activo', background='#cfe2ff')
        self.tree.tag_configure('liquidado', background='#e2e3e5')
        
        # Configurar bindings para filtros
        if hasattr(self, 'estado_combo'):
            self.estado_combo.bind('<<ComboboxSelected>>', lambda e: self.cargar_prestamos())
        if hasattr(self, 'search_var'):
            self.search_var.trace_add('write', lambda *args: self.cargar_prestamos())

        # Cargar datos iniciales
        self.cargar_prestamos()

    def mostrar_ayuda(self, event=None):
        """Muestra la ayuda contextual del módulo de empleados"""
        self.sistema_ayuda.mostrar_ayuda('prestamos')
    
    def nueva_solicitud(self):
        """Abrir formulario de nueva solicitud"""
        try:
            puede_solicitar, mensaje = self.db_manager.puede_solicitar_prestamo(
                self.usuario_actual['id_empleado']
            )
            
            if not puede_solicitar:
                messagebox.showerror("Error", mensaje)
                return

            dialog = PrestamoNuevoForm(self, self.db_manager, self.usuario_actual['id_empleado'])
            self.wait_window(dialog)
            self.cargar_prestamos()
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar la solicitud: {str(e)}")
    
    def cargar_prestamos(self):
        """Cargar la lista de préstamos según los permisos del usuario"""
        # Limpiar Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            # Obtener estado seleccionado y texto de búsqueda
            estado_filtro = self.estado_var.get() if hasattr(self, 'estado_var') else None
            texto_busqueda = self.search_var.get().lower() if hasattr(self, 'search_var') else None
            
            # Cargar préstamos según el tipo de acceso
            if self.tiene_acceso_global:
                prestamos = self.db_manager.obtener_todos_prestamos()
            else:
                prestamos = self.db_manager.obtener_prestamos_empleado(self.usuario_actual['id_empleado'])
                
            # Aplicar filtros si existen
            for prestamo in prestamos:
                # Filtrar por estado
                if estado_filtro and estado_filtro != 'Todos':
                    if prestamo['estado'].lower() != estado_filtro.lower():
                        continue
                        
                # Filtrar por texto de búsqueda
                if texto_busqueda:
                    texto_encontrado = False
                    # Buscar en todos los campos del préstamo
                    for valor in prestamo.values():
                        if str(valor).lower().find(texto_busqueda) >= 0:
                            texto_encontrado = True
                            break
                    if not texto_encontrado:
                        continue
                
                # Insertar préstamo en el Treeview
                valores = [
                    prestamo['id_prestamo'],
                    prestamo['empleado'],
                    f"{float(prestamo['monto_total']):,.2f}",
                    f"{prestamo['cuotas_pagadas']}/{prestamo['cuotas_totales']}",
                    f"{float(prestamo['monto_cuota']):,.2f}",
                    prestamo['fecha_solicitud'].strftime('%d-%m-%Y'),
                    prestamo['estado'],
                    f"{float(prestamo['saldo_restante']):,.2f}"
                ]
                
                self.tree.insert('', 'end', values=valores,
                                tags=(prestamo['estado'].lower(),))
                                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar préstamos: {str(e)}")
    
    def aprobar_prestamo(self):
        """Aprobar préstamo seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un préstamo")
            return

        prestamo = self.tree.item(selected[0])['values']
        if prestamo[6].lower() != 'pendiente': 
            messagebox.showwarning("Advertencia", 
                                "Solo se pueden aprobar préstamos pendientes")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de aprobar este préstamo?"):
            try:
                nombre_completo = f"{self.usuario_actual['nombre']} {self.usuario_actual['apellido']}"
                self.db_manager.aprobar_prestamo(
                    prestamo[0],
                    nombre_completo)
                # Registrar auditoria
                detalle = (f"Préstamo aprobado:\n"
                        f"ID Préstamo: {prestamo[0]}\n"
                        f"Aprobado por: {self.usuario_actual}\n"
                        f"Empleado: {prestamo[1]}\n"
                        f"Monto: {prestamo[2]}")

                self.db_manager.registrar_auditoria(
                    usuario=f"{self.usuario_actual['nombre']} {self.usuario_actual['apellido']}",
                    rol=f"{self.usuario_actual['rol']}",
                    accion='Aprobó Préstamo',
                    tabla='prestamos',
                    detalle=detalle)
                messagebox.showinfo("Éxito", "Préstamo aprobado correctamente")
                self.cargar_prestamos()  # Recargar después de aprobar
            except Exception as e:
                messagebox.showerror("Error", f"Error al aprobar préstamo: {str(e)}")
    
    def rechazar_prestamo(self):
        """Rechazar préstamo seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un préstamo")
            return
        
        if not self.db_manager.verificar_permiso(
            self.usuario_actual['id_usuario'], 
            'prestamos.aprobar'
        ):
            messagebox.showerror("Error", "No tiene permisos para rechazar préstamos")
            return
        
        prestamo = self.tree.item(selected[0])['values']
        if prestamo[6].lower() != 'pendiente':
            messagebox.showwarning("Advertencia", 
                                "Solo se pueden rechazar préstamos pendientes")
            return
        
        # Solicitar motivo del rechazo
        dialog = tk.Toplevel(self)
        dialog.title("Motivo del Rechazo")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="Ingrese el motivo del rechazo:").pack(pady=5)
        motivo_text = tk.Text(dialog, height=4)
        motivo_text.pack(pady=5, padx=10, fill=tk.X)
        
        def confirmar_rechazo():
            motivo = motivo_text.get("1.0", tk.END).strip()
            if not motivo:
                messagebox.showwarning("Advertencia", 
                                "Por favor ingrese el motivo del rechazo")
                return
                
            try:
                nombre_completo = f"{self.usuario_actual['nombre']} {self.usuario_actual['apellido']}"
                self.db_manager.rechazar_prestamo(
                    prestamo[0],
                    nombre_completo,
                    motivo)
                # Registrar auditoriaç
                detalle = (f"Préstamo rechazado:\n"
                        f"ID Préstamo: {prestamo[0]}\n"  
                        f"Rechazado por: {self.usuario_actual['nombre']} {self.usuario_actual['apellido']}\n"
                        f"Empleado: {prestamo[1]}\n"
                        f"Monto solicitado: {prestamo[2]}\n"
                        f"Motivo: {motivo}")

                self.db_manager.registrar_auditoria(
                    usuario=f"{self.usuario_actual['nombre']} {self.usuario_actual['apellido']}",
                    rol=f"{self.usuario_actual['rol']}",
                    accion='Rechazó préstamo',
                    tabla='prestamos',
                    detalle=detalle
                )
                messagebox.showinfo("Éxito", "Préstamo rechazado correctamente")
                dialog.destroy()
                self.cargar_prestamos()  # Recargar después de rechazar
            except Exception as e:
                messagebox.showerror("Error", f"Error al rechazar préstamo: {str(e)}")
        
        ttk.Button(dialog, text="Confirmar",
                command=confirmar_rechazo).pack(pady=10)
        ttk.Button(dialog, text="Cancelar",
                command=dialog.destroy).pack()
    
    def ver_detalles(self):
        """Ver detalles del préstamo seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un préstamo")
            return
        
        prestamo_id = self.tree.item(selected[0])['values'][0]
        PrestamoDetallesForm(self, self.db_manager, prestamo_id, self.usuario_actual)

class PrestamoDetallesForm(tk.Toplevel):
    """Formulario para ver/editar detalles de un préstamo"""
    def __init__(self, parent, db_manager, prestamo_id, usuario_actual):
        super().__init__(parent)
        self.db_manager = db_manager
        self.prestamo_id = prestamo_id
        self.usuario_actual = usuario_actual
        
        # Configuración básica
        self.title("Detalles del Préstamo")
        self.geometry("800x600")
        
        # Frame principal
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame para información general
        info_frame = ttk.LabelFrame(main_frame, text="Información General", padding="10")
        info_frame.pack(fill=tk.X, pady=5)
        
        # Campos de información
        self.info_widgets = {}
        campos = [
            ("ID:", "id_prestamo"),
            ("Empleado:", "empleado"),
            ("Monto Total:", "monto_total"),
            ("Cuotas:", "cuotas"),
            ("Cuota Quincenal:", "monto_cuota"),
            ("Saldo Pendiente:", "saldo_restante"),
            ("Estado:", "estado"),
            ("Fecha Solicitud:", "fecha_solicitud"),
            ("Fecha de Respuesta:", "fecha_aprobacion"),
            ("Atendido Por:", "aprobado_por")
        ]
        
        for i, (label, key) in enumerate(campos):
            row = i // 2
            col = i % 2 * 2
            
            ttk.Label(info_frame, text=label).grid(
                row=row, column=col, sticky='e', padx=5, pady=2)
            
            widget = ttk.Label(info_frame, text="")
            widget.grid(row=row, column=col+1, sticky='w', padx=5, pady=2)
            self.info_widgets[key] = widget
        
        # Frame para motivo/observaciones
        motivo_frame = ttk.LabelFrame(main_frame, text="Motivo/Observaciones", 
                                    padding="10")
        motivo_frame.pack(fill=tk.X, pady=5)
        
        self.motivo_text = tk.Text(motivo_frame, height=4, state='disabled')
        self.motivo_text.pack(fill=tk.X)
        
        # Frame para historial de pagos
        pagos_frame = ttk.LabelFrame(main_frame, text="Historial de Pagos", 
                                   padding="10")
        pagos_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview para pagos
        self.pagos_tree = ttk.Treeview(pagos_frame, columns=(
            "fecha", "monto", "periodo", "saldo"
        ), show='headings')
        
        # Configurar columnas
        self.pagos_tree.heading("fecha", text="Fecha")
        self.pagos_tree.heading("monto", text="Monto")
        self.pagos_tree.heading("periodo", text="Período")
        self.pagos_tree.heading("saldo", text="Saldo Restante")
        
        scrolly = ttk.Scrollbar(pagos_frame, orient=tk.VERTICAL, 
                              command=self.pagos_tree.yview)
        self.pagos_tree.configure(yscrollcommand=scrolly.set)
        
        self.pagos_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame para botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Botones según rol y estado
        if self.usuario_actual['rol'] != 'empleado':
            ttk.Button(button_frame, text="Registrar Pago",
                      command=self.registrar_pago).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Editar Detalles",
                      command=self.editar_detalles).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Cerrar",
                  command=self.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Cargar datos
        self.cargar_datos()
    
    def cargar_datos(self):
        try:
            prestamo = self.db_manager.obtener_prestamo(self.prestamo_id)
            if not prestamo:
                raise ValueError("No se encontró el préstamo")
                
            info = {
                'id_prestamo': prestamo.get('id_prestamo', ''),
                'empleado': prestamo.get('empleado', ''),
                'monto_total': f"Bs. {float(prestamo.get('monto_total', 0)):,.2f}",
                'cuotas': f"{prestamo.get('cuotas_pagadas', 0)}/{prestamo.get('cuotas_totales', 0)}",
                'monto_cuota': f"Bs. {float(prestamo.get('monto_cuota', 0)):,.2f}",
                'saldo_restante': f"Bs. {float(prestamo.get('saldo_restante', 0)):,.2f}",
                'estado': prestamo.get('estado', '').capitalize(),
                'fecha_solicitud': datetime.strptime(str(prestamo.get('fecha_solicitud', '-')), '%Y-%m-%d').strftime('%d-%m-%Y') if prestamo.get('fecha_solicitud') != '-' else '-',
                'fecha_aprobacion': datetime.strptime(str(prestamo.get('fecha_aprobacion', '-')), '%Y-%m-%d').strftime('%d-%m-%Y') if prestamo.get('fecha_aprobacion') != '-' else '-',
                'aprobado_por': prestamo.get('aprobado_por', '-')
            }

            for key, widget in self.info_widgets.items():
                widget.configure(text=info.get(key, ''))
            
            self.motivo_text.configure(state='normal')
            self.motivo_text.delete("1.0", tk.END)
            self.motivo_text.insert("1.0", prestamo.get('motivo', ''))
            self.motivo_text.configure(state='disabled')
            
            self.cargar_pagos()
                
        except Exception as e:
            print(f"Error detallado: {e}")
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
    
    def cargar_pagos(self):
        """Cargar historial de pagos"""
        # Limpiar Treeview
        for item in self.pagos_tree.get_children():
            self.pagos_tree.delete(item)
        
        # Obtener y mostrar pagos
        pagos = self.db_manager.obtener_pagos_prestamo(self.prestamo_id)
        for pago in pagos:
            valores = [
                pago['fecha'],
                f"Bs. {float(pago['monto']):,.2f}",
                pago['periodo'],
                f"Bs. {float(pago['saldo']):,.2f}"
            ]
            self.pagos_tree.insert('', 'end', values=valores)
    
    def registrar_pago(self):
        """Registrar un nuevo pago"""
        prestamo = self.db_manager.obtener_prestamo(self.prestamo_id)
        if prestamo['estado'] not in ['aprobado', 'en_pago']:
            messagebox.showwarning(
                "Advertencia", 
                "Solo se pueden registrar pagos de préstamos aprobados o en pago")
            return
        
        # Crear diálogo para pago
        dialog = tk.Toplevel(self)
        dialog.title("Registrar Pago")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Monto:").pack(pady=5)
        monto_entry = ttk.Entry(dialog)
        monto_entry.pack(pady=5)
        monto_entry.insert(0, str(prestamo['monto_cuota']))
        
        ttk.Label(dialog, text="Fecha:").pack(pady=5)
        fecha_entry = DateEntry(dialog, date_pattern='dd-mm-yyyy')
        fecha_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Período:").pack(pady=5)
        periodo_entry = ttk.Entry(dialog)
        periodo_entry.pack(pady=5)
        
        def confirmar_pago():
            try:
                monto = Decimal(monto_entry.get())
                if monto <= 0:
                    raise ValueError("El monto debe ser mayor a cero")
                    
                if monto > prestamo['saldo_restante']:
                    raise ValueError("El monto no puede ser mayor al saldo pendiente")
                    
                datos_pago = {
                    'id_prestamo': self.prestamo_id,
                    'monto': monto,
                    'fecha': fecha_entry.get_date(),
                    'periodo': periodo_entry.get().strip(),
                    'registrado_por': self.usuario_actual['usuario']
                }
                
                self.db_manager.registrar_pago_prestamo(datos_pago)
                messagebox.showinfo("Éxito", "Pago registrado correctamente")
                dialog.destroy()
                self.cargar_datos()
                
            except ValueError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Error al registrar pago: {str(e)}")
        
        ttk.Button(dialog, text="Confirmar",
                  command=confirmar_pago).pack(pady=10)
        ttk.Button(dialog, text="Cancelar",
                  command=dialog.destroy).pack()
    
    def editar_detalles(self):
        """Editar detalles del préstamo"""
        prestamo = self.db_manager.obtener_prestamo(self.prestamo_id)
        if prestamo['estado'] not in ['pendiente', 'aprobado']:
            messagebox.showwarning(
                "Advertencia", 
                "Solo se pueden editar préstamos pendientes o aprobados")
            return
        
        # Crear diálogo para edición
        dialog = tk.Toplevel(self)
        dialog.title("Editar Préstamo")
        dialog.geometry("500x400")
        
        ttk.Label(dialog, text="Monto Total:").pack(pady=5)
        monto_entry = ttk.Entry(dialog)
        monto_entry.pack(pady=5)
        monto_entry.insert(0, str(prestamo['monto_total']))
        
        ttk.Label(dialog, text="Número de Cuotas:").pack(pady=5)
        cuotas_entry = ttk.Entry(dialog)
        cuotas_entry.pack(pady=5)
        cuotas_entry.insert(0, str(prestamo['cuotas_totales']))
        
        ttk.Label(dialog, text="Observaciones:").pack(pady=5)
        obs_text = tk.Text(dialog, height=4)
        obs_text.pack(pady=5)
        obs_text.insert("1.0", prestamo['motivo'])
        
        def confirmar_edicion():
            try:
                nuevo_monto = Decimal(monto_entry.get())
                nuevas_cuotas = int(cuotas_entry.get())
                
                if nuevo_monto <= 0:
                    raise ValueError("El monto debe ser mayor a cero")
                if nuevas_cuotas <= 0:
                    raise ValueError("El número de cuotas debe ser mayor a cero")
                
                datos_actualizacion = {
                    'monto_total': nuevo_monto,
                    'cuotas_totales': nuevas_cuotas,
                    'monto_cuota': nuevo_monto / Decimal(str(nuevas_cuotas)),
                    'motivo': obs_text.get("1.0", tk.END).strip(),
                    'modificado_por': self.usuario_actual['usuario']
                }
                
                self.db_manager.actualizar_prestamo(self.prestamo_id, 
                                                  datos_actualizacion)
                messagebox.showinfo("Éxito", "Préstamo actualizado correctamente")
                dialog.destroy()
                self.cargar_datos()
                
            except ValueError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", 
                                   f"Error al actualizar préstamo: {str(e)}")
        
        ttk.Button(dialog, text="Confirmar",
                  command=confirmar_edicion).pack(pady=10)
        ttk.Button(dialog, text="Cancelar",
                  command=dialog.destroy).pack()