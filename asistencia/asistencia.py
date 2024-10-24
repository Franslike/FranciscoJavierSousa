import mysql.connector
from smartcard.System import readers
from datetime import datetime
import flet as ft
import asyncio

# Conectar a MySQL
def connect_db():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='admin',
        database='nominadb'
    )
    cursor = conn.cursor()
    return conn, cursor

# Detectar la lectura de la tarjeta NFC
def read_nfc():
    try:
        r = readers()
        if len(r) == 0:
            print("No se detectó ningún lector NFC")
            return None
        reader = r[0]
        connection = reader.createConnection()
        connection.connect()

        card_data, sw1, sw2 = connection.transmit([0xFF, 0xCA, 0x00, 0x00, 0x00])
        tarjeta_id = ''.join(format(x, '02X') for x in card_data)
        return tarjeta_id
    except Exception as e:
        print(f"Error al leer la tarjeta: {e}")
        return None

# Registrar la asistencia y actualizar la interfaz
def registrar_asistencia(cursor, conn, tarjeta_id, status_label, last_read_time, bloqueado, page):
    ahora = datetime.now()

    if bloqueado['estado'] and (ahora - last_read_time['time']).total_seconds() < 5:
        return

    cursor.execute("SELECT id_empleado, nombre, apellido FROM empleados WHERE uid_nfc = %s", (tarjeta_id,))
    empleado = cursor.fetchone()

    if empleado is None:
        status_label.value = f"No se encontró ningún empleado con la tarjeta {tarjeta_id}"
        status_label.color = ft.colors.RED
        page.update()
        return

    id_empleado, nombre, apellido = empleado

    cursor.execute("SELECT entrada, salida FROM asistencias WHERE id_empleado = %s ORDER BY entrada DESC LIMIT 1", (id_empleado,))
    ultima_asistencia = cursor.fetchone()

    ahora_str = ahora.strftime('%Y-%m-%d %H:%M:%S')

    if ultima_asistencia is None or ultima_asistencia[1] is not None:
        cursor.execute("INSERT INTO asistencias (nombre, entrada, id_empleado) VALUES (%s, %s, %s)", (nombre, ahora_str, id_empleado))
        conn.commit()
        status_label.value = f"Bienvenido {nombre} {apellido}"
        status_label.color = ft.colors.GREEN
    else:
        cursor.execute("UPDATE asistencias SET salida = %s WHERE id_empleado = %s AND salida IS NULL", (ahora_str, id_empleado))
        conn.commit()
        status_label.value = f"Hasta luego {nombre} {apellido}"
        status_label.color = ft.colors.BLUE

    last_read_time['time'] = ahora
    bloqueado['estado'] = True

    page.call_later(5, lambda: [desbloquear(bloqueado), reset_status(status_label, page)])

# Resetear el mensaje de estado
def reset_status(status_label, page):
    status_label.value = "Esperando lectura de tarjeta NFC..."
    status_label.color = ft.colors.BLACK
    page.update()

# Desbloquear las lecturas
def desbloquear(bloqueado):
    bloqueado['estado'] = False

# Función asíncrona para manejar la lectura periódica de la tarjeta NFC
async def esperar_tarjeta(cursor, conn, status_label, last_read_time, bloqueado, page):
    while True:
        tarjeta_id = read_nfc()
        if tarjeta_id:
            registrar_asistencia(cursor, conn, tarjeta_id, status_label, last_read_time, bloqueado, page)
        await asyncio.sleep(1)  # Espera 1 segundo antes de volver a leer

# Interfaz gráfica en Flet
def main(page: ft.Page):
    page.title = "Sistema de Registro de Asistencia NFC"
    conn, cursor = connect_db()

    status_label = ft.Text(value="Esperando lectura de tarjeta NFC...", size=24)

    last_read_time = {'time': datetime.now()}
    bloqueado = {'estado': False}

    # Ejecuta la tarea asíncrona para la lectura periódica
    page.add(status_label)
    page.update()

    asyncio.run(esperar_tarjeta(cursor, conn, status_label, last_read_time, bloqueado, page))

# Ejecutar la aplicación en Flet
if __name__ == "__main__":
    ft.app(target=main)
