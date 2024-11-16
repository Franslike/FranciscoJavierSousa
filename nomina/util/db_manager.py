from decimal import Decimal
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

class DatabaseManager:
    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password

    def connect(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if connection.is_connected():
                print(f"Conectado exitosamente a la base de datos: {self.database}")
                return connection
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
        return None

    def verify_credentials(self, usuario, contraseña):
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                query = "SELECT * FROM usuarios WHERE usuario = %s AND contraseña = %s"
                cursor.execute(query, (usuario, contraseña))
                result = cursor.fetchone()
                return result is not None
            except Error as e:
                print(f"Error: {e}")
                return False
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return False
    
    def registrar_empleado(self, nombre, cargo, salario, uid_nfc, fecha_contratacion, 
                      cedula_identidad, apellido, direccion=None, fecha_nacimiento=None):
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                INSERT INTO empleados (
                    nombre, cargo, salario, uid_nfc, fecha_contratacion, 
                    cedula_identidad, apellido, direccion, fecha_nacimiento
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    nombre, cargo, salario, uid_nfc, fecha_contratacion,
                    cedula_identidad, apellido, direccion, fecha_nacimiento
                ))
                connection.commit()
                print("Empleado registrado exitosamente")
            except Error as e:
                print(f"Error al registrar empleado: {e}")
                raise
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    def verificar_empleado_existente(self, cedula):
        """Verificar si ya existe un empleado con la cédula dada"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                SELECT * FROM empleados WHERE cedula_identidad = %s
                """
                cursor.execute(query, (cedula,))
                return cursor.fetchone() is not None
            except Error as e:
                print(f"Error al verificar empleado existente: {e}")
                return False
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return False
    
    def verificar_dispositivo_existente(self, uid):
        """Verificar si ya existe un dispositivo NFC con el UID dado"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                SELECT * FROM nfc_dispositivos WHERE uid = %s
                """
                cursor.execute(query, (uid,))
                return cursor.fetchone() is not None
            except Error as e:
                print(f"Error al verificar dispositivo existente: {e}")
                return False
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return False
    
    def obtener_dispositivos_empleado(self, id_empleado):
        """Obtener todos los dispositivos NFC asociados a un empleado"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                query = """
                SELECT n.tipo, n.uid, n.estado
                FROM nfc_dispositivos n
                JOIN empleado_nfc en ON n.id_dispositivo = en.id_dispositivo
                WHERE en.id_empleado = %s AND en.activo = TRUE
                """
                cursor.execute(query, (id_empleado,))
                return cursor.fetchall()
            except Error as e:
                print(f"Error al obtener dispositivos del empleado: {e}")
                return []
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return []

    def ver_empleados(self):
        """Obtener lista de empleados"""
        connection = self.connect()
        empleados = []
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                SELECT id_empleado, nombre, apellido, cedula_identidad, 
                    cargo, salario, fecha_contratacion, 
                    COALESCE(status, 'activo') as status 
                FROM empleados
                """
                cursor.execute(query)
                empleados = cursor.fetchall()
            except Error as e:
                print(f"Error al obtener empleados: {e}")
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return empleados
    
    def obtener_empleado(self, id_empleado):
        """Obtener todos los datos de un empleado específico"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                SELECT id_empleado, nombre, apellido, cedula_identidad, cargo, 
                    salario, fecha_contratacion, 
                    direccion, fecha_nacimiento,
                    COALESCE(status, 'activo') as status
                FROM empleados 
                WHERE id_empleado = %s
                """
                cursor.execute(query, (id_empleado,))
                result = cursor.fetchone()
                
                if result:
                    # Convertir a diccionario para mejor manejo
                    return {
                        'id_empleado': result[0],
                        'nombre': result[1],
                        'apellido': result[2],
                        'cedula': result[3],
                        'cargo': result[4],
                        'salario': result[5],
                        'fecha_contratacion': result[6],
                        'direccion': result[7] if result[7] else '',
                        'fecha_nacimiento': result[8],
                        'status': result[9]
                    }
                return None
            except Error as e:
                print(f"Error al obtener empleado: {e}")
                raise
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return None

    def actualizar_empleado(self, id_empleado, datos):
        """Actualizar los datos de un empleado"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                UPDATE empleados 
                SET nombre = %s, 
                    apellido = %s,
                    cargo = %s,
                    salario = %s,
                    direccion = %s,
                    fecha_nacimiento = %s,
                    fecha_contratacion = %s,
                    status = %s
                WHERE id_empleado = %s
                """
                valores = (
                    datos['nombre'],
                    datos['apellido'],
                    datos['cargo'],
                    datos['salario'],
                    datos['direccion'],
                    datos['fecha_nacimiento'],
                    datos['fecha_contratacion'],
                    datos['status'],
                    id_empleado
                )
                cursor.execute(query, valores)
                connection.commit()
            except Error as e:
                print(f"Error al actualizar empleado: {e}")
                raise
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
    
    def obtener_empleado_por_cedula(self, cedula):
        """Obtener información del empleado por cédula"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                SELECT id_empleado, nombre, apellido, cedula_identidad
                FROM empleados
                WHERE cedula_identidad = %s
                """
                cursor.execute(query, (cedula,))
                return cursor.fetchone()
            except Error as e:
                print(f"Error al obtener empleado: {e}")
                return None
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return None
    
    def cambiar_status_empleado(self, id_empleado, nuevo_status):
        """Cambiar el status de un empleado"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                UPDATE empleados 
                SET status = %s 
                WHERE id_empleado = %s
                """
                cursor.execute(query, (nuevo_status, id_empleado))
                connection.commit()
            except Error as e:
                print(f"Error al cambiar status del empleado: {e}")
                raise
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
    
    def generar_nomina_empleado(self, id_empleado, salario_base, deducciones, deducciones_opcionales, salario_neto):
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()

                # Insertar el reporte de nómina en la tabla de nóminas
                query_insert_nomina = """
                INSERT INTO nominas (id_empleado, salario_bruto, deducciones, deducciones_opcionales, salario_neto)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query_insert_nomina, (id_empleado, salario_base, deducciones, deducciones_opcionales, salario_neto))

                # Confirmar los cambios
                connection.commit()
                print(f"Nómina generada correctamente para el empleado con ID {id_empleado}")

            except Error as e:
                print(f"Error al generar la nómina para el empleado con ID {id_empleado}: {e}")
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    def obtener_deducciones_empleado(self, id_empleado):
        connection = self.connect()
        deducciones = []
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                SELECT d.nombre, d.porcentaje, d.tipo, COALESCE(ed.monto, 0) AS monto
                FROM deducciones d
                LEFT JOIN empleado_deducciones ed ON d.id_deduccion = ed.id_deduccion AND ed.id_empleado = %s
                """
                cursor.execute(query, (id_empleado,))
                deducciones = cursor.fetchall()
            except Error as e:
                print(f"Error al obtener las deducciones del empleado: {e}")
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return deducciones
    
    def obtener_asistencias(self, fecha_inicio, fecha_fin, id_empleado=None):
        connection = self.connect()
        registros = []
        if connection:
            try:
                cursor = connection.cursor()
                
                # Query base que genera todos los días laborables en el rango de fechas
                query = """
                WITH RECURSIVE calendario AS (
                    SELECT CAST(%s AS DATE) AS fecha
                    UNION ALL
                    SELECT DATE_ADD(fecha, INTERVAL 1 DAY)
                    FROM calendario
                    WHERE fecha < %s
                ),
                dias_laborables AS (
                    SELECT fecha
                    FROM calendario
                    WHERE DAYOFWEEK(fecha) NOT IN (1, 7)  -- Excluir sábados (7) y domingos (1)
                ),
                empleados_seleccionados AS (
                    SELECT id_empleado, nombre, apellido, cedula_identidad
                    FROM empleados
                    WHERE 1=1
                """
                
                params = [fecha_inicio, fecha_fin]
                
                if id_empleado:
                    query += " AND id_empleado = %s"
                    params.append(id_empleado)
                    
                query += """
                )
                SELECT 
                    dl.fecha,
                    CONCAT(e.nombre, ' ', e.apellido) as empleado,
                    e.cedula_identidad,
                    TIME(a.entrada) as hora_entrada,
                    TIME(a.salida) as hora_salida,
                    CASE
                        WHEN a.id IS NULL THEN 'Inasistencia'
                        WHEN a.estado = 'justificada' THEN 'Justificada'
                        WHEN a.salida IS NULL THEN 'Incompleto'
                        ELSE 'Presente'
                    END as estado,
                    COALESCE(a.observacion, '') as observacion
                FROM dias_laborables dl
                CROSS JOIN empleados_seleccionados e
                LEFT JOIN asistencias a ON DATE(a.entrada) = dl.fecha 
                    AND a.id_empleado = e.id_empleado
                ORDER BY dl.fecha DESC, empleado
                """
                
                cursor.execute(query, params)
                registros = cursor.fetchall()
                
            except Error as e:
                print(f"Error al obtener asistencias: {e}")
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return registros

    def registrar_justificacion(self, datos):
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                
                # Primero obtener el nombre del empleado
                query_empleado = """
                SELECT nombre FROM empleados WHERE id_empleado = %s
                """
                cursor.execute(query_empleado, (datos['empleado_id'],))
                nombre_empleado = cursor.fetchone()[0]
                
                # Registrar justificativo
                query_justificativo = """
                INSERT INTO justificativos 
                (id_empleado, fecha, tipo, motivo, documento_respaldo, registrado_por, observacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                valores_justificativo = (
                    datos['empleado_id'],
                    datos['fecha'],
                    datos['tipo'],
                    datos['motivo'],
                    datos['num_documento'],
                    datos['registrado_por'],
                    datos['observacion']
                )
                
                cursor.execute(query_justificativo, valores_justificativo)
                
                # Verificar si existe un registro de asistencia para ese día
                query_check = """
                SELECT id FROM asistencias 
                WHERE id_empleado = %s AND DATE(entrada) = %s
                """
                cursor.execute(query_check, (datos['empleado_id'], datos['fecha']))
                asistencia_existente = cursor.fetchone()
                
                if asistencia_existente:
                    # Actualizar registro existente
                    query_update = """
                    UPDATE asistencias 
                    SET estado = 'justificada', observacion = %s
                    WHERE id_empleado = %s AND DATE(entrada) = %s
                    """
                    cursor.execute(query_update, (
                        datos['observacion'],
                        datos['empleado_id'],
                        datos['fecha']
                    ))
                else:
                    # Crear nuevo registro de asistencia justificada
                    query_insert = """
                    INSERT INTO asistencias 
                    (nombre, id_empleado, entrada, estado, observacion)
                    VALUES (%s, %s, %s, 'justificada', %s)
                    """
                    cursor.execute(query_insert, (
                        nombre_empleado,
                        datos['empleado_id'],
                        datos['fecha'] + ' 00:00:00',  # Agregamos la hora
                        datos['observacion']
                    ))
                
                connection.commit()
                
            except Error as e:
                print(f"Error detallado: {str(e)}")
                raise
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    def obtener_justificacion(self, cedula, fecha):
        """
        Obtiene los detalles de una justificación para un empleado en una fecha específica
        
        Args:
            cedula (str): Cédula del empleado
            fecha (str): Fecha en formato YYYY-MM-DD
            
        Returns:
            tuple: (tipo, motivo, documento_respaldo, registrado_por, fecha_registro)
                o None si no se encuentra justificación
        """
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                SELECT j.tipo, j.motivo, j.documento_respaldo, 
                    j.registrado_por, j.fecha_registro
                FROM justificativos j
                JOIN empleados e ON j.id_empleado = e.id_empleado
                WHERE e.cedula_identidad = %s AND DATE(j.fecha) = %s
                """
                cursor.execute(query, (cedula, fecha))
                return cursor.fetchone()
                
            except Error as e:
                print(f"Error al obtener justificación: {e}")
                return None
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return None
        
    def obtener_inasistencias_empleado(self, id_empleado, fecha_inicio, fecha_fin):
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                
                query = """
                WITH RECURSIVE calendario AS (
                    SELECT CAST(%s AS DATE) AS fecha
                    UNION ALL
                    SELECT DATE_ADD(fecha, INTERVAL 1 DAY)
                    FROM calendario
                    WHERE fecha < %s
                ),
                dias_laborables AS (
                    SELECT fecha
                    FROM calendario
                    WHERE DAYOFWEEK(fecha) NOT IN (1, 7)
                )
                SELECT 
                    COUNT(*) as total_inasistencias,
                    GROUP_CONCAT(dl.fecha) as fechas
                FROM dias_laborables dl
                LEFT JOIN asistencias a ON DATE(a.entrada) = dl.fecha 
                    AND a.id_empleado = %s
                WHERE (a.id IS NULL OR a.salida IS NULL)
                    AND NOT EXISTS (
                        SELECT 1 FROM asistencias 
                        WHERE id_empleado = %s 
                        AND DATE(entrada) = dl.fecha 
                        AND estado = 'justificada'
                    )
                """
                
                cursor.execute(query, (fecha_inicio, fecha_fin, id_empleado, id_empleado))
                result = cursor.fetchone()
                
                inasistencias = result[0] if result[0] is not None else 0
                fechas = result[1].split(',') if result[1] else []
                
                return inasistencias, fechas
                
            except Error as e:
                print(f"Error al obtener inasistencias: {e}")
                return 0, []
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return 0, []
    
    def crear_periodo(self, fecha_inicio, fecha_fin, tipo, creado_por):
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                INSERT INTO periodos_nomina (fecha_inicio, fecha_fin, tipo, estado, creado_por)
                VALUES (%s, %s, %s, 'abierto', %s)
                """
                cursor.execute(query, (fecha_inicio, fecha_fin, tipo, creado_por))
                connection.commit()
            except Error as e:
                print(f"Error al crear período: {e}")
                raise
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    def verificar_solapamiento_periodos(self, fecha_inicio, fecha_fin):
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                
                # Primero verificamos si hay algún período abierto
                query_abierto = """
                SELECT COUNT(*) FROM periodos_nomina
                WHERE estado = 'abierto'
                """
                cursor.execute(query_abierto)
                periodos_abiertos = cursor.fetchone()[0]
                
                if periodos_abiertos > 0:
                    return True, "Ya existe un período abierto. Debe cerrar el período actual antes de crear uno nuevo."
                
                # Luego verificamos solapamiento de fechas
                query_solapamiento = """
                SELECT COUNT(*) FROM periodos_nomina
                WHERE (fecha_inicio <= %s AND fecha_fin >= %s)
                OR (fecha_inicio <= %s AND fecha_fin >= %s)
                OR (fecha_inicio >= %s AND fecha_fin <= %s)
                """
                cursor.execute(query_solapamiento, (fecha_fin, fecha_inicio, fecha_fin, fecha_inicio, fecha_inicio, fecha_fin))
                count = cursor.fetchone()[0]
                
                if count > 0:
                    return True, "El período se solapa con uno existente."
                
                return False, ""
                
            except Error as e:
                print(f"Error al verificar solapamiento: {e}")
                return True, f"Error al verificar solapamiento: {e}"
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return True, "Error de conexión a la base de datos"

    def obtener_periodos(self):
        connection = self.connect()
        periodos = []
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                SELECT id_periodo, tipo, fecha_inicio, fecha_fin, estado, creado_por
                FROM periodos_nomina
                ORDER BY fecha_inicio DESC
                """
                cursor.execute(query)
                periodos = cursor.fetchall()
            except Error as e:
                print(f"Error al obtener períodos: {e}")
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return periodos

    def cerrar_periodo(self, id_periodo, cerrado_por, motivo):
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                
                # Obtener estado actual
                cursor.execute("SELECT estado FROM periodos_nomina WHERE id_periodo = %s", (id_periodo,))
                estado_actual = cursor.fetchone()[0]
                
                if estado_actual == 'cerrado':
                    raise ValueError("El período ya está cerrado")
                
                # Actualizar estado del período
                update_query = """
                UPDATE periodos_nomina 
                SET estado = 'cerrado', fecha_cierre = NOW(), cerrado_por = %s
                WHERE id_periodo = %s
                """
                cursor.execute(update_query, (cerrado_por, id_periodo))
                
                # Registrar en historial
                historial_query = """
                INSERT INTO historial_periodos 
                (id_periodo, estado_anterior, estado_nuevo, usuario_id, motivo)
                VALUES (%s, %s, 'cerrado', %s, %s)
                """
                cursor.execute(historial_query, (id_periodo, estado_actual, cerrado_por, motivo))
                
                connection.commit()
            except Error as e:
                print(f"Error al cerrar período: {e}")
                raise
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    def obtener_historial_periodo(self, id_periodo):
        connection = self.connect()
        historial = []
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                SELECT fecha_cambio, estado_anterior, estado_nuevo, usuario_id, motivo
                FROM historial_periodos
                WHERE id_periodo = %s
                ORDER BY fecha_cambio DESC
                """
                cursor.execute(query, (id_periodo,))
                historial = cursor.fetchall()
            except Error as e:
                print(f"Error al obtener historial: {e}")
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return historial
    
    def guardar_prenomina(self, id_empleado, id_periodo, salario_bruto, deducciones, salario_neto):
        """Guardar la prenómina en la base de datos"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                
                # Verificar si ya existe una prenómina para este empleado y período
                check_query = """
                SELECT id_nomina FROM nominas 
                WHERE id_empleado = %s AND id_periodo = %s
                """
                cursor.execute(check_query, (id_empleado, id_periodo))
                existing = cursor.fetchone()
                
                if existing:
                    # Actualizar prenómina existente
                    update_query = """
                    UPDATE nominas 
                    SET salario_bruto = %s, deducciones = %s, salario_neto = %s
                    WHERE id_empleado = %s AND id_periodo = %s
                    """
                    cursor.execute(update_query, (
                        salario_bruto, deducciones, salario_neto,
                        id_empleado, id_periodo
                    ))
                else:
                    # Crear nueva prenómina
                    insert_query = """
                    INSERT INTO nominas (id_empleado, id_periodo, salario_bruto, 
                                    deducciones, salario_neto)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        id_empleado, id_periodo, salario_bruto,
                        deducciones, salario_neto
                    ))
                
                connection.commit()
                
            except Error as e:
                print(f"Error al guardar prenómina: {e}")
                raise
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    def obtener_prenominas_periodo(self, id_periodo):
        """Obtener todas las prenóminas de un período específico"""
        connection = self.connect()
        prenominas = []
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                SELECT n.id_nomina, e.nombre, e.apellido, e.cedula_identidad,
                    e.cargo, n.salario_bruto, n.deducciones, n.salario_neto
                FROM nominas n
                INNER JOIN empleados e ON n.id_empleado = e.id_empleado
                WHERE n.id_periodo = %s
                """
                cursor.execute(query, (id_periodo,))
                prenominas = cursor.fetchall()
            except Error as e:
                print(f"Error al obtener prenóminas: {e}")
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return prenominas

    def verificar_periodo_abierto(self, id_periodo):
        """Verificar si un período está abierto"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                SELECT estado FROM periodos_nomina 
                WHERE id_periodo = %s AND estado = 'abierto'
                """
                cursor.execute(query, (id_periodo,))
                result = cursor.fetchone()
                return result is not None
            except Error as e:
                print(f"Error al verificar estado del período: {e}")
                return False
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return False
    
    def obtener_uids_disponibles(self):
        """Obtener lista de UIDs NFC disponibles"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                SELECT id_dispositivo, uid 
                FROM nfc_dispositivos 
                WHERE estado = 'disponible' AND tipo = 'tarjeta'
                """
                cursor.execute(query)
                return cursor.fetchall()
            except Error as e:
                print(f"Error al obtener UIDs: {e}")
                return []
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return []
    
    def registrar_empleado_con_nfc(self, nombre, apellido, cedula, cargo, salario, 
                             fecha_contratacion, direccion, fecha_nacimiento,
                             uid_tarjeta, uid_telefono=None, permisos=None):
        """Registrar empleado con dispositivos NFC y crear usuario"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                # Iniciar transacción
                connection.start_transaction()
                
                # Registrar empleado
                query_empleado = """
                INSERT INTO empleados (
                    nombre, apellido, cedula_identidad, cargo, salario,
                    fecha_contratacion, direccion, fecha_nacimiento
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query_empleado, (
                    nombre, apellido, cedula, cargo, salario,
                    fecha_contratacion, direccion, fecha_nacimiento
                ))
                id_empleado = cursor.lastrowid
                
                # Crear usuario para el empleado
                query_usuario = """
                INSERT INTO usuarios (usuario, contraseña, rol, primer_ingreso, permisos)
                VALUES (%s, %s, %s, TRUE, %s)
                """
                # La contraseña inicial será la cédula
                import json
                permisos_json = json.dumps(permisos) if permisos else None
                cursor.execute(query_usuario, (
                    cedula,  # usuario
                    cedula,  # contraseña inicial
                    'empleado',  # rol por defecto
                    permisos_json  # permisos en formato JSON
                ))
                
                # Asignar tarjeta NFC
                if uid_tarjeta:
                    query_asignar_tarjeta = """
                    UPDATE nfc_dispositivos SET estado = 'asignado'
                    WHERE id_dispositivo = %s
                    """
                    cursor.execute(query_asignar_tarjeta, (uid_tarjeta,))
                    
                    # Crear relación empleado-tarjeta
                    query_relacion = """
                    INSERT INTO empleado_nfc (id_empleado, id_dispositivo)
                    VALUES (%s, %s)
                    """
                    cursor.execute(query_relacion, (id_empleado, uid_tarjeta))
                
                # Si hay teléfono, registrarlo
                if uid_telefono:
                    query_telefono = """
                    INSERT INTO nfc_dispositivos (uid, tipo, estado)
                    VALUES (%s, 'telefono', 'asignado')
                    """
                    cursor.execute(query_telefono, (uid_telefono,))
                    id_telefono = cursor.lastrowid
                    
                    cursor.execute(query_relacion, (id_empleado, id_telefono))
                
                connection.commit()
                return id_empleado
                
            except Error as e:
                connection.rollback()
                raise
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    def verificar_primer_ingreso(self, usuario):
        """Verificar si es el primer ingreso del usuario"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                SELECT primer_ingreso, permisos
                FROM usuarios
                WHERE usuario = %s
                """
                cursor.execute(query, (usuario,))
                result = cursor.fetchone()
                return result if result else (False, None)
            except Error as e:
                print(f"Error al verificar primer ingreso: {e}")
                return False, None
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    def cambiar_contraseña(self, usuario, nueva_contraseña):
        """Cambiar la contraseña del usuario y marcar que ya no es primer ingreso"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                UPDATE usuarios
                SET contraseña = %s, primer_ingreso = FALSE
                WHERE usuario = %s
                """
                cursor.execute(query, (nueva_contraseña, usuario))
                connection.commit()
                return True
            except Error as e:
                print(f"Error al cambiar contraseña: {e}")
                return False
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    def obtener_permisos_sistema(self):
        """Obtener lista de permisos disponibles"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                query = "SELECT * FROM permisos_sistema"
                cursor.execute(query)
                return cursor.fetchall()
            except Error as e:
                print(f"Error al obtener permisos: {e}")
                return []
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    def registrar_tarjeta_nfc(self, uid):
        """Registrar una nueva tarjeta NFC"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                INSERT INTO nfc_dispositivos (uid, tipo, estado)
                VALUES (%s, 'tarjeta', 'disponible')
                """
                cursor.execute(query, (uid,))
                connection.commit()
            except Error as e:
                print(f"Error al registrar tarjeta: {e}")
                raise
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    def obtener_todas_tarjetas(self):
        """Obtener lista de todas las tarjetas con información de asignación"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                query = """
                SELECT n.*, 
                    CONCAT(e.nombre, ' ', e.apellido) as empleado
                FROM nfc_dispositivos n
                LEFT JOIN empleado_nfc en ON n.id_dispositivo = en.id_dispositivo AND en.activo = TRUE
                LEFT JOIN empleados e ON en.id_empleado = e.id_empleado
                WHERE n.tipo = 'tarjeta'
                ORDER BY n.fecha_registro DESC
                """
                cursor.execute(query)
                return cursor.fetchall()
            except Error as e:
                print(f"Error al obtener tarjetas: {e}")
                return []
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return []

    def marcar_tarjeta_disponible(self, id_dispositivo):
        """Marcar una tarjeta como disponible"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                
                # Iniciar transacción
                connection.start_transaction()
                
                # Desactivar asignaciones actuales
                query_desactivar = """
                UPDATE empleado_nfc 
                SET activo = FALSE 
                WHERE id_dispositivo = %s
                """
                cursor.execute(query_desactivar, (id_dispositivo,))
                
                # Marcar como disponible
                query_disponible = """
                UPDATE nfc_dispositivos 
                SET estado = 'disponible' 
                WHERE id_dispositivo = %s
                """
                cursor.execute(query_disponible, (id_dispositivo,))
                
                connection.commit()
            except Error as e:
                connection.rollback()
                print(f"Error al marcar tarjeta: {e}")
                raise
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    def eliminar_tarjeta(self, id_dispositivo):
        """Eliminar una tarjeta no asignada"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                DELETE FROM nfc_dispositivos 
                WHERE id_dispositivo = %s 
                AND estado = 'disponible'
                """
                cursor.execute(query, (id_dispositivo,))
                connection.commit()
                
                if cursor.rowcount == 0:
                    raise Exception("No se puede eliminar una tarjeta asignada")
                    
            except Error as e:
                print(f"Error al eliminar tarjeta: {e}")
                raise
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    def obtener_tarjetas_disponibles(self):
        """Obtener tarjetas NFC disponibles"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                SELECT id_dispositivo, uid
                FROM nfc_dispositivos
                WHERE tipo = 'tarjeta' 
                AND estado = 'disponible'
                """
                cursor.execute(query)
                return cursor.fetchall()
            except Error as e:
                print(f"Error al obtener tarjetas: {e}")
                return []
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return []

    def registrar_telefono(self, uid):
        """Registrar un nuevo teléfono como dispositivo NFC"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                INSERT INTO nfc_dispositivos (uid, tipo, estado)
                VALUES (%s, 'telefono', 'disponible')
                """
                cursor.execute(query, (uid,))
                connection.commit()
                return cursor.lastrowid
            except Error as e:
                print(f"Error al registrar teléfono: {e}")
                raise
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    def asignar_dispositivo(self, id_empleado, id_dispositivo):
        """Asignar un dispositivo NFC a un empleado"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                
                # Iniciar transacción
                connection.start_transaction()
                
                # Actualizar estado del dispositivo
                query_update = """
                UPDATE nfc_dispositivos 
                SET estado = 'asignado'
                WHERE id_dispositivo = %s
                """
                cursor.execute(query_update, (id_dispositivo,))
                
                # Crear relación empleado-dispositivo
                query_insert = """
                INSERT INTO empleado_nfc (id_empleado, id_dispositivo)
                VALUES (%s, %s)
                """
                cursor.execute(query_insert, (id_empleado, id_dispositivo))
                
                connection.commit()
            except Error as e:
                connection.rollback()
                print(f"Error al asignar dispositivo: {e}")
                raise
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    def desasignar_dispositivo(self, id_empleado, uid):
        """Desasignar un dispositivo NFC de un empleado"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                
                # Iniciar transacción
                connection.start_transaction()
                
                # Obtener id_dispositivo y tipo
                query_get_device = """
                SELECT id_dispositivo, tipo 
                FROM nfc_dispositivos 
                WHERE uid = %s
                """
                cursor.execute(query_get_device, (uid,))
                result = cursor.fetchone()
                
                if result:
                    id_dispositivo, tipo = result
                    
                    # Primero eliminar la relación en empleado_nfc
                    query_delete_rel = """
                    DELETE FROM empleado_nfc 
                    WHERE id_empleado = %s AND id_dispositivo = %s
                    """
                    cursor.execute(query_delete_rel, (id_empleado, id_dispositivo))
                    
                    if tipo == 'telefono':
                        # Si es teléfono, eliminar el dispositivo
                        query_delete = """
                        DELETE FROM nfc_dispositivos 
                        WHERE id_dispositivo = %s
                        """
                        cursor.execute(query_delete, (id_dispositivo,))
                    else:
                        # Si es tarjeta, solo marcar como disponible
                        query_update_dev = """
                        UPDATE nfc_dispositivos 
                        SET estado = 'disponible'
                        WHERE id_dispositivo = %s
                        """
                        cursor.execute(query_update_dev, (id_dispositivo,))
                    
                    connection.commit()
                else:
                    raise ValueError("Dispositivo no encontrado")
                    
            except Error as e:
                connection.rollback()
                print(f"Error al desasignar dispositivo: {e}")
                raise
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    def registrar_prestamo(self, datos_prestamo):
        """Registrar un nuevo préstamo"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                INSERT INTO prestamos (
                    id_empleado, monto_total, monto_cuota, cuotas_totales,
                    saldo_restante, fecha_solicitud, estado, observaciones
                ) VALUES (%s, %s, %s, %s, %s, %s, 'pendiente', %s)
                """
                valores = (
                    datos_prestamo['id_empleado'],
                    datos_prestamo['monto_total'],
                    datos_prestamo['monto_cuota'],
                    datos_prestamo['cuotas_totales'],
                    datos_prestamo['monto_total'],  # saldo inicial es el monto total
                    datos_prestamo['fecha_solicitud'],
                    datos_prestamo['motivo']
                )
                cursor.execute(query, valores)
                connection.commit()
                
            except Error as e:
                print(f"Error al registrar préstamo: {e}")
                raise
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    def obtener_prestamos_empleado(self, id_empleado):
        """Obtener préstamos de un empleado específico"""
        connection = self.connect()
        prestamos = []
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                query = """
                SELECT p.*, 
                    CONCAT(e.nombre, ' ', e.apellido) as empleado
                FROM prestamos p
                INNER JOIN empleados e ON p.id_empleado = e.id_empleado
                WHERE p.id_empleado = %s
                ORDER BY p.fecha_solicitud DESC
                """
                cursor.execute(query, (id_empleado,))
                prestamos = cursor.fetchall()
            except Error as e:
                print(f"Error al obtener préstamos: {e}")
                return []
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return prestamos

    def obtener_todos_prestamos(self):
        """Obtener todos los préstamos"""
        connection = self.connect()
        prestamos = []
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                query = """
                SELECT p.*, 
                    CONCAT(e.nombre, ' ', e.apellido) as empleado
                FROM prestamos p
                INNER JOIN empleados e ON p.id_empleado = e.id_empleado
                ORDER BY p.fecha_solicitud DESC
                """
                cursor.execute(query)
                prestamos = cursor.fetchall()
            except Error as e:
                print(f"Error al obtener préstamos: {e}")
                return []
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return prestamos

    def obtener_prestamo(self, id_prestamo):
        """Obtener detalles de un préstamo específico"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                query = """
                SELECT p.*, 
                    CONCAT(e.nombre, ' ', e.apellido) as empleado
                FROM prestamos p
                INNER JOIN empleados e ON p.id_empleado = e.id_empleado
                WHERE p.id_prestamo = %s
                """
                cursor.execute(query, (id_prestamo,))
                return cursor.fetchone()
            except Error as e:
                print(f"Error al obtener préstamo: {e}")
                raise
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()