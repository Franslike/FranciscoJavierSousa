import mysql.connector
from smartcard.System import readers
from datetime import datetime
import tkinter as tk

# Conectar a MySQL
def connect_db():
    conn = mysql.connector.connect(
        host='localhost',       # Cambia estos valores según tu configuración
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

        # Leer el ID de la tarjeta (UID)
        card_data, sw1, sw2 = connection.transmit([0xFF, 0xCA, 0x00, 0x00, 0x00])
        tarjeta_id = ''.join(format(x, '02X') for x in card_data)
        return tarjeta_id
    except Exception as e:
        print(f"Error al leer la tarjeta: {e}")
        return None

# Registrar la asistencia y actualizar la interfaz
def registrar_asistencia(cursor, conn, tarjeta_id, label_status, last_read_time, bloqueado):
    ahora = datetime.now()

    # Bloqueo temporal de 5 segundos después de una lectura
    if bloqueado['estado'] and (ahora - last_read_time['time']).total_seconds() < 5:
        return  # Ignorar lectura si está bloqueado

    # Buscar el empleado con este UID de la tarjeta
    cursor.execute("SELECT id_empleado, nombre, apellido FROM empleados WHERE uid_nfc = %s", (tarjeta_id,))
    empleado = cursor.fetchone()

    if empleado is None:
        label_status.config(text=f"No se encontró ningún empleado con la tarjeta {tarjeta_id}", fg="red")
        return

    id_empleado, nombre, apellido = empleado

    # Buscar la última asistencia del empleado
    cursor.execute("SELECT entrada, salida FROM asistencias WHERE id_empleado = %s ORDER BY entrada DESC LIMIT 1", (id_empleado,))
    ultima_asistencia = cursor.fetchone()

    ahora_str = ahora.strftime('%Y-%m-%d %H:%M:%S')

    if ultima_asistencia is None or ultima_asistencia[1] is not None:  # Si no hay asistencia o la última tiene salida
        # Registrar una nueva entrada
        cursor.execute("INSERT INTO asistencias (nombre, entrada, id_empleado) VALUES (%s, %s, %s)", (nombre, ahora_str, id_empleado))
        conn.commit()
        label_status.config(text=f"Bienvenido {nombre} {apellido}", fg="green")
    else:
        # Actualizar la salida en la última asistencia
        cursor.execute("UPDATE asistencias SET salida = %s WHERE id_empleado = %s AND salida IS NULL", (ahora_str, id_empleado))
        conn.commit()
        label_status.config(text=f"Hasta luego {nombre} {apellido}", fg="blue")

    # Actualizar el tiempo de la última lectura y activar el bloqueo
    last_read_time['time'] = ahora
    bloqueado['estado'] = True

    # Después de 5 segundos, volver al mensaje original y desactivar el bloqueo
    label_status.after(5000, lambda: [label_status.config(text="Esperando lectura de tarjeta NFC...", fg="black"),
                                      desbloquear(bloqueado)])

# Desbloquear las lecturas después del retardo
def desbloquear(bloqueado):
    bloqueado['estado'] = False

# Función principal para la interfaz gráfica
def main():
    conn, cursor = connect_db()

    # Crear la ventana de la interfaz
    root = tk.Tk()
    root.title("Sistema de Registro de Asistencia NFC")
    root.geometry("400x200")

    label_status = tk.Label(root, text="Esperando lectura de tarjeta NFC...", font=("Arial", 14))
    label_status.pack(pady=50)

    # Variables para gestionar el bloqueo temporal
    last_read_time = {'time': datetime.now()}
    bloqueado = {'estado': False}

    # Función que actualiza la interfaz y espera la tarjeta
    def esperar_tarjeta():
        tarjeta_id = read_nfc()
        if tarjeta_id:
            registrar_asistencia(cursor, conn, tarjeta_id, label_status, last_read_time, bloqueado)
        root.after(1000, esperar_tarjeta)  # Repetir cada segundo

    root.after(1000, esperar_tarjeta)
    root.mainloop()

if __name__ == "__main__":
    main()
