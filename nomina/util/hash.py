import bcrypt
from db_manager import DatabaseManager
from config import DB_CONFIG

def hash_password(password):
    """Convierte una contraseña en texto plano a hash bcrypt"""
    # Generar el salt y hashear la contraseña
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')  # Convertir bytes a string para almacenar en la BD

def update_passwords():
    """Actualiza todas las contraseñas en la base de datos a hash bcrypt"""
    db = DatabaseManager(**DB_CONFIG)
    
    try:
        # Obtener todos los usuarios
        query_select = "SELECT id_usuario, contraseña FROM usuarios"
        usuarios = db.fetch_all(query_select)
        
        # Actualizar cada contraseña
        query_update = "UPDATE usuarios SET contraseña = %s WHERE id_usuario = %s"
        
        for user_id, plain_password in usuarios:
            # Solo actualizar si la contraseña parece estar en texto plano
            if not plain_password.startswith('$2b$'):  # Las contraseñas bcrypt empiezan con $2b$
                hashed_password = hash_password(plain_password)
                db.execute(query_update, (hashed_password, user_id))
                print(f"Actualizada contraseña para usuario ID: {user_id}")
        
        print("Proceso completado exitosamente")
        
    except Exception as e:
        print(f"Error durante la actualización: {e}")

if __name__ == "__main__":
    # Pedir confirmación antes de proceder
    print("¡ADVERTENCIA! Este script actualizará todas las contraseñas en texto plano a hash bcrypt.")
    print("Asegúrate de tener un respaldo de la base de datos antes de continuar.")
    confirm = input("¿Deseas continuar? (s/n): ")
    
    if confirm.lower() == 's':
        update_passwords()
    else:
        print("Operación cancelada")