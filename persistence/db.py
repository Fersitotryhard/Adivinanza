import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Las credenciales se leen desde el archivo .env
def get_connection() -> pymysql.connections.Connection:
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "db_adivinanza"),
        charset="utf8mb4"
    )
