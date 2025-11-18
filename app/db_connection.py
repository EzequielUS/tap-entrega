import mysql.connector
from .config import Config

class DBConnection:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def __enter__(self):
        """Método de contexto: se ejecuta al iniciar el bloque 'with'."""
        try:
            self.connection = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                port=Config.DB_PORT
            )
            self.cursor = self.connection.cursor(dictionary=True)
            return self
        except mysql.connector.Error as err:
            print(f"Error al conectar a MySQL: {err}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Método de contexto: se ejecuta al finalizar el bloque 'with'."""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            if exc_type is None:
                self.connection.commit()
            else:
                self.connection.rollback()
            self.connection.close()

    def fetch_all(self, query, params=None):
        """Ejecuta una consulta SELECT y retorna todos los resultados."""
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()

    def execute(self, query, params=None):
        """Ejecuta una consulta INSERT/UPDATE/DELETE."""
        self.cursor.execute(query, params or ())
        return self.cursor.lastrowid