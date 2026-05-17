import os
import pymysql
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "db_adivinanza"),
        charset="utf8mb4"
    )

fernet = Fernet(os.getenv("FERNET_KEY").encode())

def encrypt(text: str) -> str:
    return fernet.encrypt(text.encode()).decode()

# Adivinanzas de los 5 niveles
RIDDLES = [
    ("Chase.png", "Orejas largas, rabo cortito, corro y salto muy ligerito.", "conejo", 1),
    ("Chase.png", "Soy amarillo, alargado y los monos me adoran.", "platano", 2),
    ("Chase.png", "Tengo rayas negras y blancas y vivo en la sabana africana.", "cebra", 3),
    ("Chase.png", "Soy el animal más grande del mundo y vivo en el océano.", "ballena", 4),
    ("Chase.png", "Tengo una joroba en el lomo y camino por el desierto.", "camello", 5),
]

def seed():
    conn = get_connection()
    cursor = conn.cursor()

    print("Insertando adivinanzas...")
    for image, hint, answer, level in RIDDLES:
        encrypted = encrypt(answer)
        cursor.execute(
            "INSERT INTO riddle (image, hint, answer, level, is_active) VALUES (%s, %s, %s, %s, 1)",
            (image, hint, encrypted, level)
        )
        print(f"  Nivel {level} | respuesta: '{answer}'")

    conn.commit()
    cursor.close()
    conn.close()
    print("Listo!")

if __name__ == "__main__":
    seed()