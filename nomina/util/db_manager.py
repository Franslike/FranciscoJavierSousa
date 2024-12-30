from decimal import Decimal
from datetime import datetime
import bcrypt
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
    
    def ejecutar_query(self, query, params=None, fetchone=False, dictionary=False, commit=False):
        """Ejecuta una consulta SQL y retorna los resultados"""
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor(dictionary=dictionary)
                # Asegurarse de que query sea un string y eliminar cualquier comilla extra
                query = str(query).strip('"\'')
                cursor.execute(query, params or ())
                
                if commit:
                    connection.commit()
                
                if fetchone:
                    return cursor.fetchone()
                return cursor.fetchall()
                
            except Error as e:
                print(f"Error ejecutando query: {e}")
                raise
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    def verify_credentials(self, usuario, contraseña):
        query = """
        SELECT u.contraseña, u.id_usuario, u.rol, e.nombre, e.apellido,
            u.intentos_fallidos, u.estado
        FROM usuarios u
        LEFT JOIN empleados e ON u.id_empleado = e.id_empleado
        WHERE u.usuario = %s
        """
        
        try:
            result = self.ejecutar_query(query, (usuario,), fetchone=True)
            
            if not result:
                return False
                
            estado = result[6]
            intentos = result[5]
            
            if estado == 'bloqueado':
                raise Exception("Usuario bloqueado por seguridad. Diríjase a la opción ¿Olvidó su contraseña?.")
            elif estado == 'inactivo':
                raise Exception("Usuario inactivo. Contacte al administrador.")
                
            stored_hash = result[0].encode('utf-8')
            if bcrypt.checkpw(contraseña, stored_hash):
                # Actualizar último acceso y reiniciar intentos
                update_query = """
                UPDATE usuarios 
                SET intentos_fallidos = 0,
                    ultimo_acceso = NOW()
                WHERE usuario = %s
                """
                self.ejecutar_query(update_query, (usuario,), commit=True)
                
                self.current_user = {
                    'id': result[1],
                    'rol': result[2],
                    'nombre': result[3],
                    'apellido': result[4]
                }
                return True
            else:
                intentos += 1
                nuevo_estado = 'bloqueado' if intentos >= 3 else 'activo'
                
                self.ejecutar_query(
                    "UPDATE usuarios SET intentos_fallidos = %s, estado = %s WHERE usuario = %s",
                    (intentos, nuevo_estado, usuario),
                    commit=True
                )
                
                if nuevo_estado == 'bloqueado':
                    raise Exception("Usuario bloqueado por exceder intentos permitidos.")
                elif intentos == 2:
                    raise Exception("¡Advertencia! Este es su último intento antes de que su usuario sea bloqueado.")
                    
                return False
                
        except Exception as e:
            print(f"Error en verify_credentials: {str(e)}")
            raise

    def obtener_datos_usuario(self, usuario):
        """Obtener nombre y rol de un usuario específico"""
        query = """
        SELECT CONCAT(e.nombre, ' ', e.apellido) as nombre, u.rol
        FROM usuarios u
        INNER JOIN empleados e ON u.usuario = e.cedula_identidad
        WHERE u.usuario = %s
        """
        return self.ejecutar_query(query, params=(usuario,), fetchone=True, dictionary=True)
    
    def registrar_empleado(self, nombre, cargo, salario, uid_nfc, fecha_contratacion, 
                      cedula_identidad, apellido, direccion=None, fecha_nacimiento=None):
        
        query = """
        INSERT INTO empleados (
        nombre, cargo, salario, uid_nfc, fecha_contratacion,
        cedula_identidad, apellido, direccion, fecha_nacimiento
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.ejecutar_query(query, (nombre, cargo, salario, uid_nfc, fecha_contratacion,
                                    cedula_identidad, apellido, direccion, fecha_nacimiento), commit=True)
        print("Empleado registrado exitosamente")
        
    def verificar_empleado_existente(self, cedula):

        query = "SELECT * FROM empleados WHERE cedula_identidad = %s"
        return self.ejecutar_query(query, (cedula,), fetchone=True) is not None
    
    def verificar_dispositivo_existente(self, uid):

        query = "SELECT * FROM nfc_dispositivos WHERE uid = %s"
        return self.ejecutar_query(query, (uid,), fetchone=True) is not None
    
    def obtener_dispositivos_empleado(self, id_empleado):

        query = """
        SELECT n.tipo, n.uid, n.estado
        FROM nfc_dispositivos n
        JOIN empleado_nfc en ON n.id_dispositivo = en.id_dispositivo
        WHERE en.id_empleado = %s AND en.activo = TRUE
        """
        return self.ejecutar_query(query, (id_empleado,), dictionary=True)

    def ver_empleados(self):

        query ="""
        SELECT id_empleado, nombre, apellido, cedula_identidad,
            cargo, salario, DATE_FORMAT(fecha_contratacion, '%d-%m-%Y') as fecha_contratacion,
            COALESCE(status, 'activo') as status
        FROM empleados
        """
        return self.ejecutar_query(query)
    
    def obtener_empleado(self, id_empleado):
        query = """
        SELECT id_empleado, nombre, apellido, cedula_identidad, cargo,
            salario, fecha_contratacion, direccion, fecha_nacimiento,
            COALESCE(status, 'activo') as status, telefono    
        FROM empleados
        WHERE id_empleado = %s
        """
        result = self.ejecutar_query(query, (id_empleado,), fetchone=True)
        if result:
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
                'status': result[9],
                'telefono': result[10]
            }
        
    def actualizar_empleado(self, id_empleado, datos):
        """Actualizar los datos de un empleado"""
        query = """
        UPDATE empleados 
        SET nombre = %s, 
            apellido = %s,
            cargo = %s,
            salario = %s,
            telefono = %s,
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
            datos['telefono'],
            datos['direccion'],
            datos['fecha_nacimiento'],
            datos['fecha_contratacion'],
            datos['status'],
            id_empleado
        )
        self.ejecutar_query(query, valores, commit=True)
    
    def obtener_empleado_por_cedula(self, cedula):

        query = """
        SELECT id_empleado, nombre, apellido, cedula_identidad
        FROM empleados
        WHERE cedula_identidad = %s
        """
        return self.ejecutar_query(query, (cedula,), fetchone=True)
     
    def cambiar_status_empleado(self, id_empleado, nuevo_status, motivo):
        """
        Actualiza el status del empleado, su usuario asociado y dispositivos NFC asignados
        """
        connection = self.connect()
        if not connection:
            raise ValueError("No se pudo conectar a la base de datos")
            
        try:
            cursor = connection.cursor()
            connection.start_transaction()
            
            # Obtener información actual
            query_info = """
            SELECT e.status, u.id_usuario, u.estado
            FROM empleados e
            LEFT JOIN usuarios u ON e.id_empleado = u.id_empleado
            WHERE e.id_empleado = %s
            """
            cursor.execute(query_info, (id_empleado,))
            result = cursor.fetchone()
            
            if not result:
                raise ValueError("Empleado no encontrado")
                
            status_actual, id_usuario, estado_usuario_actual = result
            
            # Actualizar status del empleado
            query_empleado = """
            UPDATE empleados 
            SET status = %s 
            WHERE id_empleado = %s
            """
            cursor.execute(query_empleado, (nuevo_status, id_empleado))
            
            # Actualizar estado, usuario asociado
            if id_usuario:
                estado_usuario = 'activo' if nuevo_status == 'activo' else 'inactivo'
                query_usuario = """
                UPDATE usuarios 
                SET estado = %s 
                WHERE id_usuario = %s
                """
                cursor.execute(query_usuario, (estado_usuario, id_usuario))
                
                # Registrar en historial de usuarios
                query_historial = """
                INSERT INTO historial_usuarios 
                (id_usuario, estado_anterior, estado_nuevo, motivo, fecha_cambio)
                VALUES (%s, %s, %s, %s, NOW())
                """
                cursor.execute(query_historial, (
                    id_usuario,
                    estado_usuario_actual,
                    estado_usuario,
                    f"Cambio automático: {motivo}"))
            
            # Manejar dispositivos NFC
            if nuevo_status == 'inactivo':
                # Primero obtener los dispositivos actualmente asignados
                query_dispositivos = """
                SELECT n.id_dispositivo, n.uid
                FROM nfc_dispositivos n
                JOIN empleado_nfc en ON n.id_dispositivo = en.id_dispositivo
                WHERE en.id_empleado = %s AND en.activo = TRUE
                """
                cursor.execute(query_dispositivos, (id_empleado,))
                dispositivos = cursor.fetchall()
                
                for id_dispositivo, uid in dispositivos:
                    # Desactivar la asignación actual
                    query_desactivar = """
                    UPDATE empleado_nfc 
                    SET activo = FALSE,
                        fecha_desactivacion = NOW()
                    WHERE id_empleado = %s 
                    AND id_dispositivo = %s 
                    AND activo = TRUE
                    """
                    cursor.execute(query_desactivar, (id_empleado, id_dispositivo))
                    
                    # Cambiar estado del dispositivo a 'suspendido'
                    query_suspender = """
                    UPDATE nfc_dispositivos 
                    SET estado = 'suspendido',
                        observacion = %s
                    WHERE id_dispositivo = %s
                    """
                    cursor.execute(query_suspender, (
                        f"Suspendido automáticamente: {motivo}",
                        id_dispositivo))
                    
                    # Registrar en historial de dispositivos
                    query_historial_nfc = """
                    INSERT INTO historial_nfc 
                    (id_dispositivo, estado_anterior, estado_nuevo, motivo, fecha_cambio)
                    VALUES (%s, 'asignado', 'suspendido', %s, NOW())
                    """
                    cursor.execute(query_historial_nfc, (
                        id_dispositivo,
                        f"Suspensión automática por inactividad del empleado: {motivo}"))
            
            elif nuevo_status == 'activo':
                # Reactivar dispositivos suspendidos
                query_dispositivos = """
                SELECT n.id_dispositivo
                FROM nfc_dispositivos n
                JOIN empleado_nfc en ON n.id_dispositivo = en.id_dispositivo
                WHERE en.id_empleado = %s 
                AND n.estado = 'suspendido'
                """
                cursor.execute(query_dispositivos, (id_empleado,))
                dispositivos = cursor.fetchall()
                
                for (id_dispositivo,) in dispositivos:
                    # Reactivar el dispositivo
                    query_reactivar = """
                    UPDATE nfc_dispositivos 
                    SET estado = 'asignado',
                        observacion = NULL
                    WHERE id_dispositivo = %s
                    """
                    cursor.execute(query_reactivar, (id_dispositivo,))
                    
                    # Reactivar la asignación
                    query_activar = """
                    UPDATE empleado_nfc 
                    SET activo = TRUE,
                        fecha_desactivacion = NULL
                    WHERE id_empleado = %s 
                    AND id_dispositivo = %s
                    """
                    cursor.execute(query_activar, (id_empleado, id_dispositivo))
                    
                    # Registrar en historial
                    query_historial_nfc = """
                    INSERT INTO historial_nfc 
                    (id_dispositivo, estado_anterior, estado_nuevo, motivo, fecha_cambio)
                    VALUES (%s, 'suspendido', 'asignado', %s, NOW())
                    """
                    cursor.execute(query_historial_nfc, (
                        id_dispositivo,
                        f"Reactivación automática por activación del empleado: {motivo}"))
            
            # Registrar en historial de empleados
            query_historial_empleado = """
            INSERT INTO historial_empleados 
            (id_empleado, status_anterior, status_nuevo, motivo, fecha_cambio)
            VALUES (%s, %s, %s, %s, NOW())
            """
            cursor.execute(query_historial_empleado, (
                id_empleado,
                status_actual,
                nuevo_status,
                motivo))
            
            self.registrar_auditoria(
                usuario='sistema',  # O pasar el usuario como parámetro adicional
                accion='UPDATE',
                tabla='empleados',
                detalle=(f"Cambio de status de empleado ID: {id_empleado} "
                        f"de {status_actual} a {nuevo_status}. "
                        f"Motivo: {motivo}"))
            connection.commit()
            
        except Exception as e:
            if connection:
                connection.rollback()
            raise Exception(f"Error al cambiar el status: {str(e)}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def obtener_deducciones_empleado(self, id_empleado):

            query = """
            SELECT d.nombre, d.porcentaje, d.tipo, COALESCE(ed.monto, 0) AS monto
            FROM deducciones d
            LEFT JOIN empleado_deducciones ed ON d.id_deduccion = ed.id_deduccion AND ed.id_empleado = %s
            """
            return self.ejecutar_query(query, params=(id_empleado,))
    
    def obtener_asistencias(self, fecha_inicio, fecha_fin, id_empleado=None):
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

        # Ejecutar el query utilizando el método genérico
        return self.ejecutar_query(query, params=params)
    
    def registrar_justificacion(self, datos):

        # Primero obtener el nombre del empleado
        query_empleado = """
        SELECT nombre FROM empleados WHERE id_empleado = %s
        """
        empleado = self.ejecutar_query(query_empleado, params=(datos['empleado_id'],), fetchone=True)
        if not empleado:
            raise ValueError("Empleado no encontrado")
        nombre_empleado = empleado[0]

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
        self.ejecutar_query(query_justificativo, params=valores_justificativo, commit=True)

        # Verificar si existe un registro de asistencia para ese día
        query_check = """
        SELECT id FROM asistencias 
        WHERE id_empleado = %s AND DATE(entrada) = %s
        """
        asistencia_existente = self.ejecutar_query(query_check, params=(datos['empleado_id'], datos['fecha']), fetchone=True)

        if asistencia_existente:
            # Actualizar registro existente
            query_update = """
            UPDATE asistencias 
            SET estado = 'justificada', observacion = %s
            WHERE id_empleado = %s AND DATE(entrada) = %s
            """
            self.ejecutar_query(query_update, params=(datos['observacion'], datos['empleado_id'], datos['fecha']), commit=True)
        else:
            # Crear nuevo registro de asistencia justificada
            query_insert = """
            INSERT INTO asistencias 
            (nombre, id_empleado, entrada, estado, observacion)
            VALUES (%s, %s, %s, 'justificada', %s)
            """
            self.ejecutar_query(query_insert, params=(
                nombre_empleado,
                datos['empleado_id'],
                datos['fecha'] + ' 00:00:00',  # Agregar la hora
                datos['observacion']
            ), commit=True)

    def obtener_justificacion(self, cedula, fecha):
        
        query = """
        SELECT j.tipo, j.motivo, j.documento_respaldo,
            j.registrado_por, j.fecha_registro
        FROM justificativos j
        JOIN empleados e ON j.id_empleado = e.id_empleado
        WHERE e.cedula_identidad = %s AND DATE(j.fecha) = %s
        """
        return self.ejecutar_query(query, params=(cedula, fecha), fetchone=True)
        
    def obtener_inasistencias_empleado(self, id_empleado, fecha_inicio, fecha_fin):

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
        # Ejecutar el query y obtener el resultado
        result = self.ejecutar_query(query, params=(fecha_inicio, fecha_fin, id_empleado, id_empleado), fetchone=True)

        # Manejar el resultado
        if result:
            inasistencias = result[0] if result[0] is not None else 0
            fechas = result[1].split(',') if result[1] else []
            return inasistencias, fechas
        return 0, []
    
    def crear_periodo(self, fecha_inicio, fecha_fin, tipo, creado_por):

        query = """
        INSERT INTO periodos_nomina (fecha_inicio, fecha_fin, tipo, estado, creado_por)
        VALUES (%s, %s, %s, 'abierto', %s)
        """
        self.ejecutar_query(query, (fecha_inicio, fecha_fin, tipo, creado_por), commit=True)

    def verificar_solapamiento_periodos(self, fecha_inicio, fecha_fin):

        # Verificar si hay algún período abierto
        query_abierto = """
        SELECT COUNT(*) FROM periodos_nomina
        WHERE estado = 'abierto'
        """
        periodos_abiertos = self.ejecutar_query(query_abierto, fetchone=True)[0]

        if periodos_abiertos > 0:
            return True, "Ya existe un período abierto. Debe cerrar el período actual antes de crear uno nuevo."

        # Verificar solapamiento de fechas
        query_solapamiento = """
        SELECT COUNT(*) FROM periodos_nomina
        WHERE (fecha_inicio <= %s AND fecha_fin >= %s)
        OR (fecha_inicio <= %s AND fecha_fin >= %s)
        OR (fecha_inicio >= %s AND fecha_fin <= %s)
        """
        count = self.ejecutar_query(
            query_solapamiento,
            params=(fecha_fin, fecha_inicio, fecha_fin, fecha_inicio, fecha_inicio, fecha_fin),
            fetchone=True
        )[0]

        if count > 0:
            return True, "El período se solapa con uno existente."

        return False, ""
    
    def obtener_periodos(self):

        query= """
        SELECT id_periodo, tipo, fecha_inicio, fecha_fin, estado, creado_por
        FROM periodos_nomina
        ORDER BY fecha_inicio DESC
        """
        return self.ejecutar_query(query)

    def cerrar_periodo(self, id_periodo, cerrado_por, motivo):

        # Obtener estado actual del período
        estado_actual_query = """
        SELECT estado FROM periodos_nomina WHERE id_periodo = %s
        """
        estado_actual = self.ejecutar_query(estado_actual_query, params=(id_periodo,), fetchone=True)

        if not estado_actual:
            raise ValueError("El período no existe.")
        if estado_actual[0] == 'cerrado':
            raise ValueError("El período ya está cerrado.")

        # Actualizar estado del período
        update_query = """
        UPDATE periodos_nomina 
        SET estado = 'cerrado', fecha_cierre = NOW(), cerrado_por = %s
        WHERE id_periodo = %s
        """
        self.ejecutar_query(update_query, params=(cerrado_por, id_periodo), commit=True)

        # Registrar en el historial de cambios
        historial_query = """
        INSERT INTO historial_periodos 
        (id_periodo, estado_anterior, estado_nuevo, usuario_id, motivo)
        VALUES (%s, %s, 'cerrado', %s, %s)
        """
        self.ejecutar_query(
            historial_query,
            params=(id_periodo, estado_actual[0], cerrado_por, motivo),
            commit=True)

    def obtener_historial_periodo(self, id_periodo):

        query = """
        SELECT fecha_cambio, estado_anterior, estado_nuevo, usuario_id, motivo
        FROM historial_periodos
        WHERE id_periodo = %s
        ORDER BY fecha_cambio DESC
        """
        return self.ejecutar_query(query, params=(id_periodo,))
    
    def obtener_uids_disponibles(self):

        query = """
        SELECT id_dispositivo, uid
        FROM nfc_dispositivos
        WHERE estado = 'disponible' AND tipo = 'tarjeta'
        """
        return self.ejecutar_query(query)
    
    def registrar_empleado_con_nfc(self, nombre, apellido, cedula, telefono, cargo, salario, 
                                fecha_contratacion, direccion, fecha_nacimiento,
                                uid_tarjeta, uid_telefono=None, permisos=None):
        
        # Mapeo de cargos a roles
        CARGO_TO_ROL = {
            'Gerente': 'gerente',
            'Supervisor': 'admin',
            'Analista': 'analista',
            'Empleado': 'empleado'
        }
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                connection.start_transaction()
                
                # Registrar empleado
                query_empleado = """
                INSERT INTO empleados (
                    nombre, apellido, cedula_identidad, telefono, cargo, salario,
                    fecha_contratacion, direccion, fecha_nacimiento
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query_empleado, (
                    nombre, apellido, cedula, telefono, cargo, salario,
                    fecha_contratacion, direccion, fecha_nacimiento
                ))
                id_empleado = cursor.lastrowid
                
                # Obtener rol basado en el cargo
                rol = CARGO_TO_ROL.get(cargo, 'empleado')  # 'empleado' como valor por defecto
                
                # Crear usuario con el rol correspondiente al cargo
                query_usuario = """
                INSERT INTO usuarios (usuario, contraseña, rol, primer_ingreso, id_empleado)
                VALUES (%s, %s, %s, TRUE, %s)
                """
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(cedula.encode('utf-8'), salt)
                
                cursor.execute(query_usuario, (
                    cedula,
                    hashed_password.decode('utf-8'),
                    rol,
                    id_empleado
                ))
                id_usuario = cursor.lastrowid
                
                # Asignar permisos si existen
                if permisos:
                    for codigo in permisos:
                        query_permiso = """
                        INSERT INTO usuario_permisos (id_usuario, id_permiso, asignado_por)
                        SELECT %s, id_permiso, 'admin'
                        FROM permisos_sistema 
                        WHERE codigo = %s
                        """
                        cursor.execute(query_permiso, (id_usuario, codigo))
                
                # Asignar tarjeta NFC si existe
                if uid_tarjeta:
                    query_tarjeta = """
                    UPDATE nfc_dispositivos 
                    SET estado = 'asignado'
                    WHERE id_dispositivo = %s
                    """
                    cursor.execute(query_tarjeta, (uid_tarjeta,))
                    
                    query_relacion = """
                    INSERT INTO empleado_nfc (id_empleado, id_dispositivo)
                    VALUES (%s, %s)
                    """
                    cursor.execute(query_relacion, (id_empleado, uid_tarjeta))
                
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

        query_user = """
        SELECT id_usuario, primer_ingreso
        FROM usuarios
        WHERE usuario = %s
        """

        user_result = self.ejecutar_query(query_user, (usuario,), fetchone=True)

        if not user_result:
            return False, []
        
        # Obtenemos los permisos del usuario
        query_permisos = """
        SELECT ps.codigo
        FROM permisos_sistema ps
        JOIN usuario_permisos up ON ps.id_permiso = up.id_permiso
        WHERE up.id_usuario = %s
        """
        permisos_result = self.ejecutar_query(query_permisos, (user_result[0],))
        permisos = [p[0] for p in permisos_result]
        
        return user_result[1], permisos

    def cambiar_contraseña(self, usuario, nueva_contraseña):
        
        """Cambiar la contraseña del usuario y marcar que ya no es primer ingreso"""
        query = """
        UPDATE usuarios
        SET contraseña = %s, primer_ingreso = FALSE
        WHERE usuario = %s
        """
        try:
            self.ejecutar_query(query, params=(nueva_contraseña, usuario), commit=True)
            return True
        except Error as e:
            print(f"Error al cambiar contraseña: {e}")
            return False
        
    def obtener_permisos_sistema(self):

        """Obtener lista de permisos disponibles"""
        query = "SELECT * FROM permisos_sistema"
        return self.ejecutar_query(query, dictionary=True)

    def registrar_tarjeta_nfc(self, uid):

        """Registrar una nueva tarjeta NFC"""
        query = """
        INSERT INTO nfc_dispositivos (uid, tipo, estado)
        VALUES (%s, 'tarjeta', 'disponible')
        """
        try:
            self.ejecutar_query(query, params=(uid,), commit=True)
        except Error as e:
            print(f"Error al registrar tarjeta: {e}")
            raise

    def obtener_todas_tarjetas(self):

        """Obtener lista de todas las tarjetas con información de asignación"""
        query = """
        SELECT n.*, 
            CONCAT(e.nombre, ' ', e.apellido) as empleado
        FROM nfc_dispositivos n
        LEFT JOIN empleado_nfc en ON n.id_dispositivo = en.id_dispositivo AND en.activo = TRUE
        LEFT JOIN empleados e ON en.id_empleado = e.id_empleado
        WHERE n.tipo = 'tarjeta'
        ORDER BY n.fecha_registro DESC
        """
        return self.ejecutar_query(query, dictionary=True)

    def marcar_tarjeta_disponible(self, id_dispositivo):
        """Marcar una tarjeta como disponible"""
        connection = self.connect()
        if not connection:
            raise ValueError("No se pudo conectar a la base de datos.")
        try:
            # Iniciar transacción
            connection.start_transaction()
            cursor = connection.cursor()

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

            # Confirmar cambios
            connection.commit()
        except Error as e:
            # Revertir cambios si ocurre un error
            connection.rollback()
            print(f"Error al marcar tarjeta: {e}")
            raise
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def eliminar_tarjeta(self, id_dispositivo):
        """Eliminar una tarjeta no asignada"""
        query = """
        DELETE FROM nfc_dispositivos 
        WHERE id_dispositivo = %s 
        AND estado = 'disponible'
        """
        try:
            connection = self.connect()
            if not connection:
                raise ValueError("No se pudo conectar a la base de datos.")
            
            # Ejecutar el query
            cursor = connection.cursor()
            cursor.execute(query, (id_dispositivo,))
            connection.commit()

            # Verificar si se eliminó alguna tarjeta
            if cursor.rowcount == 0:
                raise Exception("No se puede eliminar una tarjeta asignada")
        except Error as e:
            print(f"Error al eliminar tarjeta: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def obtener_tarjetas_disponibles(self):

        """Obtener tarjetas NFC disponibles"""
        query = """
        SELECT id_dispositivo, uid
        FROM nfc_dispositivos
        WHERE tipo = 'tarjeta' 
        AND estado = 'disponible'
        """
        return self.ejecutar_query(query)

    def asignar_dispositivo(self, id_empleado, id_dispositivo):
        """Asignar un dispositivo NFC a un empleado"""
        connection = self.connect()
        if not connection:
            raise ValueError("No se pudo conectar a la base de datos.")
        try:
            # Iniciar transacción
            connection.start_transaction()
            cursor = connection.cursor()

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

            # Confirmar transacción
            connection.commit()
        except Error as e:
            # Revertir cambios si ocurre un error
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
        if not connection:
            raise ValueError("No se pudo conectar a la base de datos.")
        try:
            # Iniciar transacción
            connection.start_transaction()
            cursor = connection.cursor()

            # Obtener id_dispositivo y tipo
            query_get_device = """
            SELECT id_dispositivo, tipo 
            FROM nfc_dispositivos 
            WHERE uid = %s
            """
            cursor.execute(query_get_device, (uid,))
            result = cursor.fetchone()

            if not result:
                raise ValueError("Dispositivo no encontrado")
            
            id_dispositivo, tipo = result

            # Eliminar relación en empleado_nfc
            query_delete_rel = """
            DELETE FROM empleado_nfc 
            WHERE id_empleado = %s AND id_dispositivo = %s
            """
            cursor.execute(query_delete_rel, (id_empleado, id_dispositivo))

            # Si es tarjeta, marcar como disponible
            query_update_dev = """
            UPDATE nfc_dispositivos 
            SET estado = 'disponible'
            WHERE id_dispositivo = %s
            """
            cursor.execute(query_update_dev, (id_dispositivo,))

            # Confirmar transacción
            connection.commit()
        except Error as e:
            # Revertir cambios si ocurre un error
            connection.rollback()
            print(f"Error al desasignar dispositivo: {e}")
            raise
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def registrar_prestamo(self, datos_prestamo):
        """Registrar un nuevo préstamo"""
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
        try:
            self.ejecutar_query(query, params=valores, commit=True)
        except Error as e:
            print(f"Error al registrar préstamo: {e}")
            raise
        
    def obtener_prestamos_empleado(self, id_empleado):
        """Obtener préstamos de un empleado específico"""
        query = """
        SELECT p.id_prestamo,
            CONCAT(e.nombre, ' ', e.apellido) as empleado,
            p.monto_total,
            p.cuotas_pagadas,
            p.cuotas_totales,
            p.monto_cuota,
            p.saldo_restante,
            p.estado,
            p.fecha_solicitud,
            COALESCE(p.fecha_aprobacion, '-') as fecha_aprobacion,
            COALESCE(p.aprobado_por, '-') as aprobado_por,
            p.observaciones as motivo
        FROM prestamos p
        INNER JOIN empleados e ON p.id_empleado = e.id_empleado
        WHERE p.id_empleado = %s
        ORDER BY p.fecha_solicitud DESC
        """
        try:
            return self.ejecutar_query(query, params=(id_empleado,), dictionary=True)
        except Exception as e:
            print(f"Error al obtener préstamos del empleado: {e}")
            return []
        
    def obtener_prestamos_monto_nomina(self, id_empleado):
        """Obtener monto total de préstamos activos para la nómina"""
        query = """
        SELECT COALESCE(SUM(monto_cuota), 0) as total_cuotas
        FROM prestamos 
        WHERE id_empleado = %s 
        AND estado IN ('aprobado', 'activo')
        """
        result = self.ejecutar_query(query, (id_empleado,), fetchone=True)
        return Decimal(str(result[0])) if result and result[0] else Decimal('0')

    def obtener_todos_prestamos(self):
        """Obtener todos los préstamos"""
        query = """
        SELECT p.*, 
            CONCAT(e.nombre, ' ', e.apellido) as empleado
        FROM prestamos p
        INNER JOIN empleados e ON p.id_empleado = e.id_empleado
        ORDER BY p.fecha_solicitud DESC
        """
        try:
            return self.ejecutar_query(query, dictionary=True)
        except Error as e:
            print(f"Error al obtener préstamos: {e}")
            return []
        
    def obtener_pagos_prestamo(self, id_prestamo):
        """Obtener el historial de pagos de un préstamo"""
        query = """
        SELECT 
            DATE_FORMAT(fecha_pago, '%Y-%m-%d') as fecha,
            monto_pagado as monto,
            COALESCE(CAST(id_nomina AS CHAR), 'Manual') as periodo,
            saldo_restante as saldo
        FROM prestamos_pagos 
        WHERE id_prestamo = %s
        ORDER BY fecha_pago DESC
        """
        try:
            return self.ejecutar_query(query, (id_prestamo,), dictionary=True)
        except Exception as e:
            print(f"Error al obtener pagos: {e}")
            return []

    def obtener_prestamo(self, id_prestamo):
        query = """
        SELECT p.id_prestamo, 
            p.monto_total,
            p.monto_cuota,
            p.cuotas_pagadas,
            p.cuotas_totales,
            p.saldo_restante,
            p.estado,
            CONCAT(e.nombre, ' ', e.apellido) as empleado,
            p.observaciones as motivo,
            COALESCE(DATE_FORMAT(p.fecha_solicitud, '%Y-%m-%d'), '-') as fecha_solicitud,
            COALESCE(DATE_FORMAT(p.fecha_aprobacion, '%Y-%m-%d'), '-') as fecha_aprobacion,
            COALESCE(p.aprobado_por, '-') as aprobado_por
        FROM prestamos p
        INNER JOIN empleados e ON p.id_empleado = e.id_empleado
        WHERE p.id_prestamo = %s
        """
        try:
            return self.ejecutar_query(query, params=(id_prestamo,), fetchone=True, dictionary=True)
        except Error as e:
            print(f"Error al obtener préstamo: {e}")
            raise

    def rechazar_prestamo(self, id_prestamo, rechazado_por, motivo):
        """Rechazar un préstamo"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            query = """
            UPDATE prestamos 
            SET estado = 'rechazado',
                observaciones = CONCAT(COALESCE(observaciones, ''), '\nRechazado por: ', %s, '\nMotivo: ', %s),
                fecha_aprobacion = NOW()
            WHERE id_prestamo = %s AND estado = 'pendiente'
            """
            cursor.execute(query, (rechazado_por, motivo, id_prestamo))
            connection.commit()
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def aprobar_prestamo(self, id_prestamo, aprobado_por):
        """Aprobar un préstamo"""
        try:
            connection = self.connect()
            cursor = connection.cursor()
            
            query = """
            UPDATE prestamos 
            SET estado = 'aprobado',
                fecha_aprobacion = NOW(),
                aprobado_por = %s
            WHERE id_prestamo = %s AND estado = 'pendiente'
            """
            cursor.execute(query, (aprobado_por, id_prestamo))
            connection.commit()
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def registrar_pago_prestamo(self, datos_pago):
        """Registra un pago de préstamo y actualiza el estado del préstamo"""
        connection = self.connect()
        if not connection:
            raise ValueError("No se pudo conectar a la base de datos")
            
        try:
            cursor = connection.cursor()
            connection.start_transaction()

            # Obtener préstamos activos del empleado
            query_prestamos = """
            SELECT p.id_prestamo, p.saldo_restante, p.cuotas_pagadas, 
                p.cuotas_totales, p.monto_cuota
            FROM prestamos p
            WHERE p.id_empleado = %s 
            AND p.estado IN ('aprobado', 'activo')
            ORDER BY p.fecha_solicitud ASC
            FOR UPDATE
            """
            cursor.execute(query_prestamos, (datos_pago['id_empleado'],))
            prestamos = cursor.fetchall()

            if not prestamos:
                raise Exception("No se encontraron préstamos activos para este empleado")

            monto_restante = Decimal(str(datos_pago['monto']))

            for prestamo in prestamos:
                id_prestamo = prestamo[0]
                saldo_actual = Decimal(str(prestamo[1]))
                cuotas_pagadas = prestamo[2]
                cuotas_totales = prestamo[3]
                monto_cuota = Decimal(str(prestamo[4]))

                # Usar el monto de la cuota exacta
                monto_pago = monto_cuota
                nuevo_saldo = saldo_actual - monto_pago
                nuevas_cuotas_pagadas = cuotas_pagadas + 1

                # Registrar el pago
                query_pago = """
                INSERT INTO prestamos_pagos 
                (id_prestamo, fecha_pago, monto_pagado, saldo_restante)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query_pago, (
                    id_prestamo,
                    datos_pago['fecha'],
                    monto_pago,
                    nuevo_saldo
                ))

                # Actualizar estado del préstamo
                nuevo_estado = 'liquidado' if nuevo_saldo <= 0 else 'activo'
                query_update = """
                UPDATE prestamos
                SET saldo_restante = %s,
                    cuotas_pagadas = %s,
                    estado = %s
                WHERE id_prestamo = %s
                """
                cursor.execute(query_update, (
                    nuevo_saldo,
                    nuevas_cuotas_pagadas,
                    nuevo_estado,
                    id_prestamo
                ))

            connection.commit()

        except Error as e:
            connection.rollback()
            raise Exception(f"Error al registrar pago: {str(e)}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def registrar_auditoria(self, usuario, accion, tabla, detalle):
        query = """
        INSERT INTO auditoria (usuario, accion, tabla, detalle)
        VALUES (%s, %s, %s, %s)
        """
        self.ejecutar_query(query, (usuario, accion, tabla, detalle), commit=True)
