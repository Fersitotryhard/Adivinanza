from werkzeug.security import generate_password_hash, check_password_hash
from enums.role import Role
from persistence.db import get_connection
import pymysql
from flask_login import UserMixin

class User(UserMixin):

    # Constructor de la clase User
    def __init__(self, id: int, name: str, email: str, password: str, role: Role, is_active: bool):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.role = role
        self._is_active = bool(is_active)

    @property
    def is_active(self) -> bool:
        return self._is_active

    
    @staticmethod
    def get_by_id(user_id: int) -> "User | None":
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT * FROM user WHERE id = %s"
            cursor.execute(sql, (user_id,))
            row = cursor.fetchone()
            cursor.close()
            connection.close()

            if row is None:
                return None

            return User(
                id=row["id"],
                name=row["name"],
                email=row["email"],
                password=row["password"],
                role=row["role"],
                is_active=row["is_active"]
            )
        except Exception as ex:
            print(f"Error getting user by id: {ex}")
            return None

    # Verifica si un correo ya está registrado en la base de datos
    # Returns: True si existe, False si no
    @staticmethod
    def check_email_exists(email: str) -> bool:
        connection = get_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT email FROM user WHERE email = %s"
        cursor.execute(sql, (email,))
        row = cursor.fetchone()
        cursor.close()
        connection.close()
        return row is not None
    
    # Guarda un nuevo usuario con contraseña hasheada
    # Returns: True si se guardó correctamente, False si hubo error
    @staticmethod
    def save(name: str, email: str, password: str) -> bool:
        try:
            connection = get_connection()
            cursor = connection.cursor()

            hash_password = generate_password_hash(password)

            sql = """
                INSERT INTO user (name, email, password, role, is_active)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (name, email, hash_password, 'player', 1))
            connection.commit()
            cursor.close()
            connection.close()
            return True

        except Exception as ex:
            print(f"Error saving user: {ex}")
            return False

    # Autentica un usuario verificando correo y contraseña
    # Returns: objeto User si es correcto, 'inactive' si está desactivado, None si falla
    @staticmethod
    def get_by_credentials(email: str, password: str):
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            sql = "SELECT * FROM user WHERE email = %s"
            cursor.execute(sql, (email,))
            row = cursor.fetchone()
            cursor.close()
            connection.close()

            if row is None:
                return None

            if not check_password_hash(row["password"], password):
                return None

            if not row["is_active"]:
                return "inactive"

            return User(
                id=row["id"],
                name=row["name"],
                email=row["email"],
                password=row["password"],
                role=row["role"],
                is_active=row["is_active"]
            )

        except Exception as ex:
            print(f"Error getting user by credentials: {ex}")
            return None

    # Obtiene todos los usuarios registrados ordenados por ID
    # Retorna: list[User]
    @staticmethod
    def get_all() -> list:
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM user ORDER BY id ASC")
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            return [User(r["id"], r["name"], r["email"], r["password"], r["role"], r["is_active"]) for r in rows]
        except Exception as ex:
            print(f"Error getting all users: {ex}")
            return []