from unittest.mock import MagicMock
from app.auth.auth_service import AuthService

def test_login_ok():
    """Prueba el login exitoso de un usuario."""
    # Configurar el mock del DAO
    usuario_dao = MagicMock()
    usuario_mock = MagicMock()
    usuario_mock.check_password.return_value = True
    usuario_mock.generate_auth_token.return_value = 'token123'
    usuario_mock.rol = 'admin'

    usuario_dao.obtener_por_username.return_value = usuario_mock

    service = AuthService(usuario_dao)
    resultado = service.login('testuser', 'correctpassword')

    assert resultado == {'token': 'token123', 'rol': 'admin'}

def test_login_usuario_inexistente():
    """Prueba el login con un usuario inexistente."""
    # Configurar el mock del DAO
    usuario_dao = MagicMock()
    usuario_dao.obtener_por_username.return_value = None

    service = AuthService(usuario_dao)
    resultado = service.login('nonexistentuser', 'anypassword')

    assert resultado is None