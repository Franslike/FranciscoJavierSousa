import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class NfcForm(ttk.Frame):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager

        self.pack(fill=tk.BOTH, expand=True)
        
        # Frame principal
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame para registro
        self.registro_frame = ttk.LabelFrame(self.main_frame, text="Registro de Tarjeta NFC", padding="10")
        self.registro_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Campos para nueva tarjeta
        ttk.Label(self.registro_frame, text="UID:").grid(row=0, column=0, padx=5, pady=5)
        self.uid_entry = ttk.Entry(self.registro_frame, width=40)
        self.uid_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Botón registrar
        ttk.Button(self.registro_frame, text="Registrar Tarjeta",
                  command=self.registrar_tarjeta).grid(row=0, column=2, padx=5, pady=5)
        
        # Nota informativa
        ttk.Label(self.registro_frame, 
                 text="Ingrese el UID en formato hexadecimal (ej: 1A2B3C4D)",
                 foreground="gray").grid(row=1, column=0, columnspan=3, padx=5, pady=5)
        
        # Frame para lista de tarjetas
        list_frame = ttk.LabelFrame(self.main_frame, text="Tarjetas NFC Registradas", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Crear Treeview
        self.tree = ttk.Treeview(list_frame, columns=(
            "id", "uid", "tipo", "estado", "fecha_registro", "empleado"),
            show='headings', displaycolumns=("uid", "tipo", "estado", "fecha_registro", "empleado"))
        
        # Configurar columnas
        self.tree.column("id", width=0, stretch=False)  # Ocultar ID
        self.tree.column("uid", width=150)
        self.tree.column("tipo", width=100)
        self.tree.column("estado", width=100)
        self.tree.column("fecha_registro", width=150)
        self.tree.column("empleado", width=200)

        # Configurar encabezados
        self.tree.heading("id", text="ID")
        self.tree.heading("uid", text="UID")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("estado", text="Estado")
        self.tree.heading("fecha_registro", text="Fecha Registro")
        self.tree.heading("empleado", text="Empleado Asignado")
        
        # Configurar colores según estado
        self.tree.tag_configure('disponible', background='#d4edda')  # Verde claro
        self.tree.tag_configure('asignado', background='#fff3cd')    # Amarillo claro
        
        # Scrollbars
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        # Frame para botones de acción
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Actualizar",
                  command=self.cargar_tarjetas).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Marcar como Disponible",
                  command=self.marcar_disponible).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar",
                  command=self.eliminar_tarjeta).pack(side=tk.LEFT, padx=5)
        
        # Cargar datos iniciales
        self.cargar_tarjetas()
    
    def registrar_tarjeta(self):
        """Registrar nueva tarjeta NFC"""
        uid = self.uid_entry.get().strip().upper()
        
        # Validaciones
        if not uid:
            messagebox.showwarning("Advertencia", "Por favor ingrese el UID")
            return
            
        if not all(c in '0123456789ABCDEF' for c in uid):
            messagebox.showerror("Error", "El UID debe estar en formato hexadecimal")
            return
            
        try:
            self.db_manager.registrar_tarjeta_nfc(uid)
            messagebox.showinfo("Éxito", "Tarjeta registrada correctamente")
            self.uid_entry.delete(0, tk.END)
            self.cargar_tarjetas()
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar tarjeta: {str(e)}")
    
    def cargar_tarjetas(self):
        """Cargar lista de tarjetas NFC"""
        # Limpiar Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Obtener tarjetas
        tarjetas = self.db_manager.obtener_todas_tarjetas()
        
        for tarjeta in tarjetas:
            valores = [
                tarjeta['id_dispositivo'],
                tarjeta['uid'],
                tarjeta['tipo'],
                tarjeta['estado'],
                tarjeta['fecha_registro'].strftime('%Y-%m-%d %H:%M'),
                tarjeta['empleado'] if tarjeta['empleado'] else 'No asignado'
            ]
            self.tree.insert('', 'end', values=valores, tags=(tarjeta['estado'],))
    
    def marcar_disponible(self):
        """Marcar una tarjeta como disponible"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione una tarjeta")
            return
        
        item = self.tree.item(selected[0])
        id_dispositivo = item['values'][0]
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de marcar esta tarjeta como disponible?"):
            try:
                self.db_manager.marcar_tarjeta_disponible(id_dispositivo)
                messagebox.showinfo("Éxito", "Tarjeta marcada como disponible")
                self.cargar_tarjetas()
            except Exception as e:
                messagebox.showerror("Error", f"Error al marcar tarjeta: {str(e)}")
    
    def eliminar_tarjeta(self):
        """Eliminar una tarjeta"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione una tarjeta")
            return
        
        item = self.tree.item(selected[0])
        id_dispositivo = item['values'][0]
        estado = item['values'][3]
        
        if estado == 'asignado':
            messagebox.showerror("Error", "No se puede eliminar una tarjeta asignada")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta tarjeta?"):
            try:
                self.db_manager.eliminar_tarjeta(id_dispositivo)
                messagebox.showinfo("Éxito", "Tarjeta eliminada correctamente")
                self.cargar_tarjetas()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar tarjeta: {str(e)}")