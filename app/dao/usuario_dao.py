from typing import TYPE_CHECKING
from ..db_connection import DBConnection
from ..models import Usuario

if TYPE_CHECKING:
    from ..auth.auth_service import AuthService

class UsuarioDAO:

    def crear(self, usuario: Usuario):
        """ Inserta un nuevo usuario en la DB y devuelve su ID. """
        query = "INSERT INTO Usuarios (username, password_hash, rol) VALUES (%s, %s, %s)"
        params = (usuario.username, usuario.password_hash, usuario.rol)

        try:
            with DBConnection() as db:
                db.cursor.execute(query, params)
                db.connection.commit()
                return db.cursor.lastrowid
        except Exception as e:
            print(f"Error al crear usuario en DB: {e}")
            return None

    def obtener_por_username(self, username):
        """ Busca un usuario por su nombre de usuario. """
        query = "SELECT * FROM Usuarios WHERE username = %s"

        with DBConnection() as db:
            db.cursor.execute(query, (username,))
            data = db.cursor.fetchone()

        if data:
            return Usuario(
                id_usuario=data['id_usuario'],
                username=data['username'],
                password_hash=data['password_hash'],
                rol=data['rol']
            )
        return None

    def obtener_todos(self):
        """ Devuelve una lista de todos los usuarios. """
        query = "SELECT * FROM Usuarios"

        with DBConnection() as db:
            db.cursor.execute(query)
            rows = db.cursor.fetchall()

        usuarios = []
        for data in rows:
            usuario = Usuario(
                id_usuario=data['id_usuario'],
                username=data['username'],
                password_hash=data['password_hash'],
                rol=data['rol']
            )
            usuarios.append(usuario)

        return usuarios