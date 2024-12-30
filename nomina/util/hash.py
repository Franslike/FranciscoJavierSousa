import bcrypt
import mysql.connector
from config import DB_CONFIG

def hash_existing_passwords():
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    
    try:
        # Get all users
        cursor.execute("SELECT id_usuario, usuario, contraseña FROM usuarios")
        users = cursor.fetchall()
        
        # Update each user's password with bcrypt hash
        for user_id, username, plain_password in users:
            # Generate salt and hash
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
            
            # Update password in database
            cursor.execute(
                "UPDATE usuarios SET contraseña = %s WHERE id_usuario = %s",
                (hashed.decode('utf-8'), user_id)
            )
            print(f"Updated password for user: {username}")
        
        connection.commit()
        print("All passwords have been hashed successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    hash_existing_passwords()