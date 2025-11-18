import bcrypt
import jwt

from flask import current_app
from datetime import datetime, timedelta, timezone

class Usuario:
    def __init__(self, id_usuario=None, username=None, password_hash=None, rol=None):
        self.id_usuario = id_usuario
        self.username = username
        self.password_hash = password_hash
        self.rol = rol

    @staticmethod
    def hash_password(password):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def generate_auth_token(self):
        secret_key = current_app.config.get('JWT_SECRET_KEY')
        expiracion = current_app.config.get('JWT_EXPIRATION_SECONDS')
        fecha_expiracion = datetime.now(timezone.utc) + timedelta(seconds=expiracion)
        fecha_utc = datetime.now(timezone.utc)
        try:
            payload = {
                'exp': fecha_expiracion,
                'iat': fecha_utc,
                'sub': str(self.id_usuario),
                'username': str(self.username),
                'rol': str(self.rol)
            }
            return jwt.encode(payload, secret_key, algorithm='HS256')
        except Exception as e:
            return str(e)

class Vehiculo:
    def __init__(self, matricula=None, id_marca=None, anio=None):
        self.matricula = matricula
        self.id_marca = id_marca
        self.anio = anio

    def to_dict(self):
        return {
            'matricula': self.matricula,
            'id_marca': self.id_marca,
            'anio': self.anio
        }

class Turno:
    def __init__(self, id_turno=None, matricula=None, fecha=None, estado='LIBRE', id_resultado=None):
        self.id_turno = id_turno
        self.matricula = matricula
        self.fecha = fecha
        self.id_resultado = id_resultado
        self.estado = estado


    def to_dict(self):
        return {
            'id_turno': self.id_turno,
            'matricula': self.matricula,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'id_resultado': self.id_resultado,
            'estado': self.estado,
        }

class Resultado:
    def __init__(self, id_resultado=None, resultado=None, puntaje_total=None, observaciones=None):
        self.id_resultado = id_resultado
        self.resultado = resultado
        self.puntaje_total = puntaje_total
        self.observaciones = observaciones

    def to_dict(self):
        return {
            'id_resultado': self.id_resultado,
            'resultado': self.resultado,
            'puntaje_total': self.puntaje_total,
            'observaciones': self.observaciones
        }

class ResultadoPorControl:
    def __init__(self, id_resultado=None, id_control=None, calificacion=None, observaciones=None):
        self.id_resultado = id_resultado
        self.id_control = id_control
        self.calificacion = calificacion
        self.observaciones = observaciones

    def to_dict(self):
        return {
            'id_resultado': self.id_resultado,
            'id_control': self.id_control,
            'calificacion': self.calificacion,
            'observaciones': self.observaciones
        }