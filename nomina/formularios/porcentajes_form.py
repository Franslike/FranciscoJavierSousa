import tkinter as tk 
from tkinter import ttk, messagebox
from datetime import datetime
from decimal import Decimal
import calendar
from util.ayuda import Ayuda

class GestionPorcentajesForm(ttk.Frame):
    def __init__(self, parent, db_manager, usuario_actual):
        super().__init__(parent)
        self.db_manager = db_manager
        self.usuario_actual = usuario_actual

        self.pack(fill=tk.BOTH, expand=True)
        
        # Frame principal
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook para pestañas
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Crear pestañas
        self.deducciones_tab = ttk.Frame(self.notebook)
        self.bonificaciones_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.deducciones_tab, text="Deducciones")
        self.notebook.add(self.bonificaciones_tab, text="Bonificaciones")
        
        # Configurar cada pestaña
        self.setup_deducciones_tab()
        self.setup_bonificaciones_tab()

    def setup_deducciones_tab(self):
        # TreeView para deducciones
        self.deducciones_tree = ttk.Treeview(self.deducciones_tab, columns=(
            "id", "nombre", "porcentaje", "tipo"
        ), show='headings')
        
        self.deducciones_tree.heading("id", text="ID")
        self.deducciones_tree.heading("nombre", text="Nombre")
        self.deducciones_tree.heading("porcentaje", text="Porcentaje")
        self.deducciones_tree.heading("tipo", text="Tipo")
        
        self.deducciones_tree.column("id", width=0, stretch=False)
        self.deducciones_tree.column("nombre", width=200)
        self.deducciones_tree.column("porcentaje", width=100)
        self.deducciones_tree.column("tipo", width=100)
        
        self.deducciones_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Botones
        btn_frame = ttk.Frame(self.deducciones_tab)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Editar",
                  command=self.editar_deduccion).pack(side=tk.LEFT, padx=5)
        
        self.cargar_deducciones()

    def setup_bonificaciones_tab(self):
        # TreeView para bonificaciones
        self.bonificaciones_tree = ttk.Treeview(self.bonificaciones_tab, columns=(
            "id", "nombre", "porcentaje", "tipo", "condicion"
        ), show='headings')
        
        self.bonificaciones_tree.heading("id", text="ID")
        self.bonificaciones_tree.heading("nombre", text="Nombre")
        self.bonificaciones_tree.heading("porcentaje", text="Porcentaje")
        self.bonificaciones_tree.heading("tipo", text="Tipo")
        self.bonificaciones_tree.heading("condicion", text="Condición")
        
        self.bonificaciones_tree.column("id", width=0, stretch=False)
        self.bonificaciones_tree.column("nombre", width=200)
        self.bonificaciones_tree.column("porcentaje", width=100)
        self.bonificaciones_tree.column("tipo", width=100)
        self.bonificaciones_tree.column("condicion", width=150)
        
        self.bonificaciones_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Botones
        btn_frame = ttk.Frame(self.bonificaciones_tab)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Editar",
                  command=self.editar_bonificacion).pack(side=tk.LEFT, padx=5)
        
        self.cargar_bonificaciones()

    def cargar_deducciones(self):
        for item in self.deducciones_tree.get_children():
            self.deducciones_tree.delete(item)
            
        query = "SELECT * FROM deducciones"
        deducciones = self.db_manager.ejecutar_query(query, dictionary=True)
        
        for d in deducciones:
            self.deducciones_tree.insert('', 'end', values=(
                d['id_deduccion'],
                d['nombre'],
                f"{float(d['porcentaje'])*100}%",
                d['tipo']
            ))

    def cargar_bonificaciones(self):
        for item in self.bonificaciones_tree.get_children():
            self.bonificaciones_tree.delete(item)
            
        query = "SELECT * FROM bonificaciones"
        bonificaciones = self.db_manager.ejecutar_query(query, dictionary=True)
        
        for b in bonificaciones:
            self.bonificaciones_tree.insert('', 'end', values=(
                b['id_bonificacion'],
                b['nombre'],
                f"{float(b['porcentaje'])*100}%",
                b['tipo'],
                b['condicion']
            ))

    def editar_deduccion(self):
        selected = self.deducciones_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione una deducción")
            return
            
        item = self.deducciones_tree.item(selected[0])
        self.mostrar_dialogo_edicion("deduccion", item['values'])

    def editar_bonificacion(self):
        selected = self.bonificaciones_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione una bonificación")
            return
            
        item = self.bonificaciones_tree.item(selected[0])
        self.mostrar_dialogo_edicion("bonificacion", item['values'])

    def mostrar_dialogo_edicion(self, tipo, valores):
        dialog = tk.Toplevel(self)
        dialog.title(f"Editar {'Deducción' if tipo == 'deduccion' else 'Bonificación'}")
        dialog.geometry("350x400")
        dialog.configure(bg='white')
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título y subtítulo
        ttk.Label(frame, 
                    text=f"Editar {'Deducción' if tipo == 'deduccion' else 'Bonificación'}", 
                    font=('Arial', 16, 'bold'),
                    foreground='#2596be').pack(anchor='center')
                    
        ttk.Label(frame,
                    text="Complete los campos para actualizar el porcentaje",
                    font=('Arial', 10),
                    foreground='#666666').pack(pady=(5,15))
                    
        # Frame para campos
        campos_frame = ttk.LabelFrame(frame, text="Datos", padding=10)
        campos_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(campos_frame, text="Porcentaje (%):").pack(pady=5)
        porcentaje_var = tk.StringVar(value=valores[2].replace('%', ''))
        porcentaje_entry = ttk.Entry(campos_frame, textvariable=porcentaje_var, width=50)
        porcentaje_entry.pack(pady=5)
        
        ttk.Label(campos_frame, text="Motivo del cambio:").pack(pady=5)
        motivo_text = tk.Text(campos_frame, height=4, width=40)
        motivo_text.pack(pady=5)

        # Botones con estilo
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)

        guardar_btn = tk.Button(
            button_frame,
            text="Guardar",
            font=("Arial", 10, "bold"),
            fg="#ffffff",
            bg="#0D6EFD",
            activebackground="#0B5ED7",
            relief="flat",
            cursor="hand2",
            width=15,
            command=lambda: guardar_cambios()
        )
        guardar_btn.pack(side=tk.LEFT, padx=5)

        cancelar_btn = tk.Button(
            button_frame,
            text="Cancelar",
            font=("Arial", 10, "bold"),
            fg="#ffffff", 
            bg="#6C757D",
            activebackground="#5C636A",
            relief="flat",
            cursor="hand2",
            width=15,
            command=dialog.destroy
        )
        cancelar_btn.pack(side=tk.LEFT, padx=5)

        # Eventos hover
        guardar_btn.bind("<Enter>", lambda e: e.widget.config(bg="#0B5ED7"))
        guardar_btn.bind("<Leave>", lambda e: e.widget.config(bg="#0D6EFD"))
        cancelar_btn.bind("<Enter>", lambda e: e.widget.config(bg="#5C636A"))
        cancelar_btn.bind("<Leave>", lambda e: e.widget.config(bg="#6C757D"))

        # Centrar ventana
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Función para guardar los cambios
        def guardar_cambios():
            if not porcentaje_var.get() or not motivo_text.get("1.0", tk.END).strip():
                messagebox.showwarning("Advertencia", "Todos los campos son requeridos")
                return
                
            try:
                nuevo_porcentaje = float(porcentaje_var.get()) / 100
                tabla = 'deducciones' if tipo == 'deduccion' else 'bonificaciones'
                id_campo = 'id_deduccion' if tipo == 'deduccion' else 'id_bonificacion'
                
                # Actualizar porcentaje en la base de datos
                query = f"""
                UPDATE {tabla}
                SET porcentaje = %s
                WHERE {id_campo} = %s
                """
                self.db_manager.ejecutar_query(query, (nuevo_porcentaje, valores[0]), commit=True)
                
                # Registrar en auditoría
                valor_anterior = float(valores[2].replace('%', '')) / 100
                detalle = (f"Actualización de porcentaje en {tabla}:\n"
                        f"Concepto: {valores[1]}\n"
                        f"Valor anterior: {valor_anterior*100}%\n"
                        f"Valor nuevo: {nuevo_porcentaje*100}%\n"
                        f"Motivo: {motivo_text.get('1.0', tk.END).strip()}")
                        
                self.db_manager.registrar_auditoria(
                    usuario=f"{self.usuario_actual['nombre']} {self.usuario_actual['apellido']}",
                    rol=f"{self.usuario_actual['rol']}",
                    accion='Actualizó porcentaje',
                    tabla=tabla,
                    detalle=detalle
                )
                
                messagebox.showinfo("Éxito", "Porcentaje actualizado correctamente")
                dialog.destroy()
                
                # Recargar datos
                if tipo == 'deduccion':
                    self.cargar_deducciones()
                else:
                    self.cargar_bonificaciones()
                    
            except ValueError:
                messagebox.showerror("Error", "El porcentaje debe ser un número válido")
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar: {str(e)}")
        
        # Botones de acción
        ttk.Button(frame, text="Guardar", command=guardar_cambios).pack(side=tk.LEFT, padx=5, pady=20)
        ttk.Button(frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5, pady=20)
