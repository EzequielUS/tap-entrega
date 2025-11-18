import os

class Config:
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'password_segura'
    DB_NAME = os.environ.get('DB_NAME') or 'db_vehiculos'
    DB_PORT = os.environ.get('DB_PORT') or 3306

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'test-token'
    JWT_EXPIRATION_SECONDS = os.environ.get('JWT_EXPIRATION_SECONDS') or 60*5 # 5 minutos