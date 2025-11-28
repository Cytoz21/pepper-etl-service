import bcrypt
import getpass

def generate_hash():
    print("=== Generador de Hash de Contraseña ===")
    password = getpass.getpass("Ingrese la contraseña que desea usar: ")
    confirm = getpass.getpass("Confirme la contraseña: ")
    
    if password != confirm:
        print("Error: Las contraseñas no coinciden")
        return

    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    
    print("\n=== Guarde estos valores en su .env o Dokploy ===")
    print(f"AUTH_PASSWORD_HASH={hashed.decode()}")
    print("===============================================")

if __name__ == "__main__":
    generate_hash()
