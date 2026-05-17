from persistence.db import get_connection
from cryptography.fernet import Fernet
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Clave de cifrado cargada desde el .env
_fernet = Fernet(os.getenv("FERNET_KEY").encode())


class Riddle:

    # Constructor de la clase Riddle
    def __init__(self, id: int, image: str, hint: str, answer: str, level: int, is_active: bool):
        self.id = id
        self.image = image
        self.hint = hint
        self.answer = answer
        self.level = level
        self.is_active = bool(is_active)

    # Cifra la palabra secreta antes de guardarla en la base de datos
    # Args: answer - palabra en texto plano
    # Returns: cadena cifrada en base64
    @staticmethod
    def encrypt_answer(answer: str) -> str:
        return _fernet.encrypt(answer.encode()).decode()

    # Descifra la palabra secreta obtenida de la base de datos
    # Args: encrypted_answer - cadena cifrada en base64
    # Returns: palabra secreta en texto plano
    @staticmethod
    def decrypt_answer(encrypted_answer: str) -> str:
        return _fernet.decrypt(encrypted_answer.encode()).decode()

    # Guarda una nueva adivinanza con la respuesta cifrada
    # Returns: True si se guardó correctamente, False si hubo error
    @staticmethod
    def save(image: str, hint: str, answer: str, level: int) -> bool:
        try:
            connection = get_connection()
            cursor = connection.cursor()

            encrypted = Riddle.encrypt_answer(answer)

            sql = """
                INSERT INTO riddle (image, hint, answer, level, is_active)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (image, hint, encrypted, level, 0))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Exception as ex:
            print(f"Error saving riddle: {ex}")
            return False

    # Obtiene la adivinanza activa para un nivel dado
    @staticmethod
    def get_active_by_level(level: int) -> "Riddle | None":
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT * FROM riddle WHERE level = %s AND is_active = 1"
            cursor.execute(sql, (level,))
            row = cursor.fetchone()
            cursor.close()
            connection.close()

            if row is None:
                return None

            return Riddle(
                id=row["id"],
                image=row["image"],
                hint=row["hint"],
                answer=Riddle.decrypt_answer(row["answer"]),
                level=row["level"],
                is_active=row["is_active"]
            )
        except Exception as ex:
            print(f"Error getting active riddle: {ex}")
            return None

    # Obtiene todas las adivinanzas ordenadas por nivel
    # Returns: lista de objetos Riddle con respuestas descifradas
    @staticmethod
    def get_all() -> list["Riddle"]:
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM riddle ORDER BY level ASC, id ASC")
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            return [
                Riddle(
                    r["id"], r["image"], r["hint"],
                    Riddle.decrypt_answer(r["answer"]),
                    r["level"], r["is_active"]
                )
                for r in rows
            ]
        except Exception as ex:
            print(f"Error getting all riddles: {ex}")
            return []

    # Activa una adivinanza y desactiva las demás del mismo nivel
    # Retorna: bool - True si se actualizó correctamente
    @staticmethod
    def set_active(riddle_id: int, level: int) -> bool:
        try:
            connection = get_connection()
            cursor = connection.cursor()

            sql_deactivate = "UPDATE riddle SET is_active = 0 WHERE level = %s"
            cursor.execute(sql_deactivate, (level,))

            sql_activate = "UPDATE riddle SET is_active = 1 WHERE id = %s"
            cursor.execute(sql_activate, (riddle_id,))

            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Exception as ex:
            print(f"Error setting active riddle: {ex}")
            return False