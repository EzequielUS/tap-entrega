
class AuthService:

    def __init__(self, usuario_dao) -> None:
        self.usuario_dao = usuario_dao

    def login(self, username: str, password: str):
        """Verifica credenciales y genera un token JWT."""
        usuario = self.usuario_dao.obtener_por_username(username)
        if usuario and usuario.check_password(password):
            token = usuario.generate_auth_token()
            return {'token': token, 'rol': usuario.rol}

        return None