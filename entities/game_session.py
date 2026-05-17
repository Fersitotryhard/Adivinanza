from persistence.db import get_connection
import pymysql

class GameSession:
    """Entidad que representa una partida de juego."""

    # Constructor de la clase GameSession
    # Args: id, user_id, total_attempts, completed, played_at
    def __init__(self, id: int, user_id: int, total_attempts: int, completed: bool, played_at: str):
        self.id = id
        self.user_id = user_id
        self.total_attempts = total_attempts
        self.completed = bool(completed)
        self.played_at = played_at

    # Guarda una nueva partida en la base de datos
    # Returns: True si se guardó correctamente, False si hubo error
    @staticmethod
    def save(user_id: int, total_attempts: int, completed: bool) -> bool:
        try:
            connection = get_connection()
            cursor = connection.cursor()
            sql = """
                INSERT INTO game_session (user_id, total_attempts, completed)
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (user_id, total_attempts, int(completed)))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Exception as ex:
            print(f"Error saving game session: {ex}")
            return False

    # Obtiene el top 5 de ganadores ordenados por menos intentos
    # Returns: lista de diccionarios con name, total_attempts y played_at
    @staticmethod
    def get_top_winners() -> list[dict]:
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            sql = """
                SELECT u.name, gs.total_attempts, gs.played_at
                FROM game_session gs
                JOIN user u ON gs.user_id = u.id
                WHERE gs.completed = 1
                ORDER BY gs.total_attempts ASC, gs.played_at ASC
                LIMIT 5
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            return rows
        except Exception as ex:
            print(f"Error getting top winners: {ex}")
            return []