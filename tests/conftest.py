import pytest
from app import create_app
from app.config import Config
from app.models import Usuario
from flask import current_app

class TestingConfig(Config):
    TESTING = True
    JWT_SECRET_KEY = 'TEST_SECRET_KEY'
    JWT_EXPIRATION_SECONDS = 60 * 60 * 24 * 7

@pytest.fixture(scope='session')
def app():
    """Fixture que crea y configura la instancia de la aplicación Flask."""
    app = create_app(config_class=TestingConfig)
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """Fixture para obtener un cliente de prueba HTTP."""
    return app.test_client()

def _generate_test_token(app, username, user_id, rol):
    """Función auxiliar para generar un token JWT válido."""
    with app.app_context():
        usuario_ficticio = Usuario(
            id_usuario=user_id,
            username=username,
            rol=rol,
            password_hash=""
        )

        token = usuario_ficticio.generate_auth_token()

        return {
            'token': token,
            'headers': {'Authorization': f'Bearer {token}'},
            'rol': rol
        }

@pytest.fixture(scope='session')
def client_token_data(app):
    """Token de prueba para el rol CLIENTE."""
    return _generate_test_token(app, "cliente_test", 1, "CLIENTE")

@pytest.fixture(scope='session')
def inspector_token_data(app):
    """Token de prueba para el rol INSPECTOR."""
    return _generate_test_token(app, "inspector_test", 2, "INSPECTOR")

@pytest.fixture
def admin_token_data(app):
    """Token de prueba para el rol ADMINISTRADOR."""
    with app.app_context():
        return _generate_test_token(app, "admin_test", 3, "ADMINISTRADOR")
