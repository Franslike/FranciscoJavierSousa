import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import calendar
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing
from decimal import Decimal
import os

class ReporteDeducciones(ttk.Frame):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.pack(fill=tk.BOTH, expand=True)

        # Frame principal
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame contenedor para tipo reporte y filtros
        top_container = ttk.Frame(self.main_frame)
        top_container.pack(fill=tk.X, padx=5, pady=5)

        # Agregar el tipo de reporte directamente
        ttk.Label(top_container, text="Tipo de Reporte:").pack(side=tk.LEFT, padx=5)
        self.tipo_reporte_combo = ttk.Combobox(top_container, values=["Deducciones"], state="readonly")
        self.tipo_reporte_combo.pack(side=tk.LEFT, padx=5)
        self.tipo_reporte_combo.set("Deducciones")

        # Frame para filtros
        self.filtros_frame = ttk.LabelFrame(self.main_frame, text="Filtros")
        self.filtros_frame.pack(fill=tk.X, padx=5, pady=5)

        # Tipo de deducción
        ttk.Label(self.filtros_frame, text="Tipo de Deducción:").pack(side=tk.LEFT, padx=5)
        self.tipo_deduccion = tk.StringVar()
        self.combo_deduccion = ttk.Combobox(self.filtros_frame, 
                                          textvariable=self.tipo_deduccion,
                                          values=["Seguro Social", "RPE", "Ley de Política Habitacional"],
                                          state="readonly",
                                          width=25)
        self.combo_deduccion.pack(side=tk.LEFT, padx=5)

        # Período
        ttk.Label(self.filtros_frame, text="Desde:").pack(side=tk.LEFT, padx=5)
        self.fecha_inicio = DateEntry(self.filtros_frame, width=12)
        self.fecha_inicio.pack(side=tk.LEFT, padx=5)

        ttk.Label(self.filtros_frame, text="Hasta:").pack(side=tk.LEFT, padx=5)
        self.fecha_fin = DateEntry(self.filtros_frame, width=12)
        self.fecha_fin.pack(side=tk.LEFT, padx=5)

        # Empleado (opcional)
        ttk.Label(self.filtros_frame, text="Empleado:").pack(side=tk.LEFT, padx=5)
        self.empleado_var = tk.StringVar()
        self.combo_empleado = ttk.Combobox(self.filtros_frame, 
                                         textvariable=self.empleado_var,
                                         state="readonly",
                                         width=30)
        self.combo_empleado.pack(side=tk.LEFT, padx=5)

        # Botón generar
        ttk.Button(self.filtros_frame, text="Generar Reporte",
                  command=self.generar_reporte).pack(side=tk.LEFT, padx=5)

        # Frame para resultados
        self.resultados_frame = ttk.LabelFrame(self.main_frame, text="Resultados", padding="5")
        self.resultados_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Treeview para mostrar resultados
        self.tree = ttk.Treeview(self.resultados_frame, columns=(
            "periodo", "empleado", "cargo", "salario", "monto_deduccion"
        ), show='headings')

        # Configurar columnas
        self.tree.heading("periodo", text="Período")
        self.tree.heading("empleado", text="Empleado")
        self.tree.heading("cargo", text="Cargo")
        self.tree.heading("salario", text="Salario Base")
        self.tree.heading("monto_deduccion", text="Monto Deducción")

        self.tree.column("periodo", width=100)
        self.tree.column("empleado", width=200)
        self.tree.column("cargo", width=100)
        self.tree.column("salario", width=100)
        self.tree.column("monto_deduccion", width=100)

        # Scrollbars
        vsb = ttk.Scrollbar(self.resultados_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.resultados_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid
        self.tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')

        # Frame para totales
        self.totales_frame = ttk.Frame(self.main_frame)
        self.totales_frame.pack(fill=tk.X, pady=5)

        # Labels para totales
        self.total_label = ttk.Label(self.totales_frame, text="Total Deducciones: Bs. 0,00")
        self.total_label.pack(side=tk.LEFT, padx=5)

        self.promedio_label = ttk.Label(self.totales_frame, text="Promedio por Empleado: Bs. 0,00")
        self.promedio_label.pack(side=tk.LEFT, padx=5)

        # Frame para botones
        self.botones_frame = ttk.Frame(self.main_frame)
        self.botones_frame.pack(fill=tk.X, pady=5)

        ttk.Button(self.botones_frame, text="Exportar a PDF",
                  command=self.exportar_pdf).pack(side=tk.LEFT, padx=5)

        # Cargar empleados
        self.cargar_empleados()

    def cargar_empleados(self):
        """Cargar lista de empleados en el combobox"""
        query = """
        SELECT CONCAT(nombre, ' ', apellido, ' - ', cedula_identidad) as empleado
        FROM empleados
        WHERE status = 'activo'
        ORDER BY nombre, apellido
        """
        empleados = self.db_manager.ejecutar_query(query)
        
        self.combo_empleado['values'] = ["Todos"] + [emp[0] for emp in empleados]
        self.combo_empleado.set("Todos")

    def generar_reporte(self):
        """Generar el reporte según los filtros seleccionados"""
        if not self.tipo_deduccion.get():
            messagebox.showwarning("Advertencia", "Por favor seleccione un tipo de deducción")
            return

        try:
            # Limpiar Treeview
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Construir query base
            query = """
            SELECT 
                p.tipo as periodo,
                DATE_FORMAT(p.fecha_inicio, '%d-%m-%Y') as fecha_inicio,
                DATE_FORMAT(p.fecha_fin, '%d-%m-%Y') as fecha_fin,
                CONCAT(e.nombre, ' ', e.apellido) as empleado,
                e.cargo,
                n.salario_base,
                n.seguro_social,
                n.rpe,
                n.ley_pol_hab
            FROM periodos_nomina p
            INNER JOIN nominas n ON p.id_periodo = n.id_periodo
            INNER JOIN empleados e ON n.id_empleado = e.id_empleado
            WHERE p.fecha_inicio >= %s 
            AND p.fecha_fin <= %s
            AND p.estado = 'cerrado'
            AND n.estado = 'procesada'
            """

            params = [self.fecha_inicio.get_date(), self.fecha_fin.get_date()]

            # Filtrar por empleado si está seleccionado
            if self.empleado_var.get() != "Todos":
                cedula = self.empleado_var.get().split(" - ")[-1]
                query += " AND e.cedula_identidad = %s"
                params.append(cedula)

            # Ordenar resultados
            query += " ORDER BY p.fecha_inicio, empleado"

            # Ejecutar consulta
            resultados = self.db_manager.ejecutar_query(query, params)

            # Variables para totales
            total_deducciones = Decimal('0')
            empleados_unicos = set()

            # Procesar resultados
            for resultado in resultados:
                periodo = f"{resultado[0]} ({resultado[1]} - {resultado[2]})"
                empleado = resultado[3]
                cargo = resultado[4]
                salario = Decimal(str(resultado[5]))
                deducciones = Decimal(str(resultado[6]))

                # Obtener deducción específica según tipo
                if self.tipo_deduccion.get() == "Seguro Social":
                    monto_deduccion = Decimal(str(resultado[6]))  # seguro_social
                elif self.tipo_deduccion.get() == "RPE":
                    monto_deduccion = Decimal(str(resultado[7]))  # rpe
                else:  # Ley de Política Habitacional
                    monto_deduccion = Decimal(str(resultado[8]))  # ley_pol_hab

                # Actualizar totales
                total_deducciones += monto_deduccion
                empleados_unicos.add(empleado)

                # Insertar en Treeview
                self.tree.insert('', 'end', values=(
                    periodo,
                    empleado,
                    cargo,
                    f"Bs. {float(salario):,.2f}",
                    f"Bs. {float(monto_deduccion):,.2f}"
                ))

            # Actualizar etiquetas de totales
            promedio = total_deducciones / len(empleados_unicos) if empleados_unicos else Decimal('0')
            self.total_label.config(text=f"Total Deducciones: Bs. {float(total_deducciones):,.2f}")
            self.promedio_label.config(text=f"Promedio por Empleado: Bs. {float(promedio):,.2f}")

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")

    def exportar_pdf(self):
        """Exportar resultados a PDF"""
        if not self.tree.get_children():
            messagebox.showwarning("Advertencia", "No hay datos para exportar")
            return

        try:
            # Crear nombre de archivo descriptivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            tipo_deduccion = self.tipo_deduccion.get().replace(" ", "_").lower()
            filename = f"reporte_deduccion_{tipo_deduccion}_{timestamp}.pdf"
            
            # Crear estructura de carpetas organizada
            output_folder = os.path.join("reportes", "deducciones")
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
                
            filepath = os.path.join(output_folder, filename)

            doc = SimpleDocTemplate(filepath, pagesize=landscape(letter))

            # Estilos
            styles = getSampleStyleSheet()
            title_style = styles['Title']
            normal_style = styles['Normal']

            # Lista de elementos para el PDF
            elements = []

            # Título
            titulo = f"Reporte de {self.tipo_deduccion.get()}"
            elements.append(Paragraph(titulo, title_style))
            elements.append(Spacer(1, 20))

            # Información de filtros
            filtros_texto = [
                f"Período: {self.fecha_inicio.get_date().strftime('%d-%m-%Y')} al {self.fecha_fin.get_date().strftime('%d-%m-%Y')}",
                f"Empleado: {self.empleado_var.get()}",
                f"Fecha de generación: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
            ]
            for texto in filtros_texto:
                elements.append(Paragraph(texto, normal_style))
            elements.append(Spacer(1, 20))

            # Datos para la tabla
            data = [['Período', 'Empleado', 'Cargo', 'Salario Base', 'Monto Deducción']]
            for item in self.tree.get_children():
                valores = self.tree.item(item)['values']
                data.append(valores)

            # Crear tabla
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 20))

            # Totales
            elements.append(Paragraph(self.total_label.cget("text"), normal_style))
            elements.append(Paragraph(self.promedio_label.cget("text"), normal_style))

            # Construir documento
            doc.build(elements)

            messagebox.showinfo("Éxito", f"Reporte exportado como {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar a PDF: {str(e)}")