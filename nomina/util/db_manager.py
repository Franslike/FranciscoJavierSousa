from decimal import Decimal
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
    
    def registrar_empleado(self, nombre, cargo, salario, uid_nfc, fecha_contratacion, cedula_identidad, apellido):
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                INSERT INTO empleados (nombre, cargo, salario, uid_nfc, fecha_contratacion, cedula_identidad, apellido)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (nombre, cargo, salario, uid_nfc, fecha_contratacion, cedula_identidad, apellido))
                connection.commit()  # Para guardar los cambios en la base de datos
                print("Empleado registrado exitosamente")
            except Error as e:
                print(f"Error al registrar empleado: {e}")
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    def verificar_empleado_existente(self, cedula_identidad, uid_nfc):
        connection = self.connect()
        if connection is None:
            print("No se pudo conectar a la base de datos")
            return False
        
        try:
            cursor = connection.cursor()
            query = """
            SELECT * FROM empleados WHERE cedula_identidad = %s OR uid_nfc = %s
            """
            cursor.execute(query, (cedula_identidad, uid_nfc))
            resultado = cursor.fetchone()  # Si hay un resultado, significa que ya existe
            return resultado is not None
        except Error as e:
                print(f"Error al verificar empleado existente: {e}")
                return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def ver_empleados(self):
        connection = self.connect()
        empleados = []
        if connection:
            try:
                cursor = connection.cursor()
                query = "SELECT id_empleado, nombre, apellido, cedula_identidad, cargo, salario, fecha_contratacion FROM empleados"
                cursor.execute(query)
                empleados = cursor.fetchall()  # Obtenemos todos los empleados
            except Error as e:
                print(f"Error al obtener empleados: {e}")
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return empleados
    
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
    
    def obtener_inasistencias_empleado(self, id_empleado):
        return 0  # O implementa la lógica real para obtener las inasistencias

    def obtener_prestamos_empleado(self, id_empleado):
        return Decimal('0')  # O implementa la lógica real para obtener los préstamos



# Obtener deducciones
# query_deducciones = "SELECT monto FROM deducciones WHERE id_empleado = %s"
# cursor.execute(query_deducciones, (id_empleado,))
# deducciones = sum([float(deduccion[0]) for deduccion in cursor.fetchall()])