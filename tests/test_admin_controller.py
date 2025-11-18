from unittest.mock import patch
from app.models import Usuario

@patch('app.admin.admin_controller.admin_service')
def test_crear_usuario_exito(mock_service, client, admin_token_data):
    """Prueba la creación de un usuario con rol de admin (éxito)."""
    mock_service.crear_usuario.return_value = (Usuario(id_usuario=1, username='nuevo_user', rol='CLIENTE'), None)

    response = client.post('/api/admin/usuarios', headers=admin_token_data['headers'], json={'username': 'nuevo_user', 'password': '123', 'rol': 'CLIENTE'})

    assert response.status_code == 201
    assert 'Usuario "nuevo_user" creado exitosamente' in response.get_json()['message']

@patch('app.admin.admin_controller.admin_service')
def test_crear_usuario_sin_autorizacion(mock_service, client, client_token_data):
    """Prueba que un usuario no-admin no pueda crear usuarios."""
    response = client.post('/api/admin/usuarios', headers=client_token_data['headers'], json={'username': 'otro_user', 'password': '123', 'rol': 'CLIENTE'})

    assert response.status_code == 403 # Forbidden

@patch('app.admin.admin_controller.admin_service')
def test_crear_usuario_parametros_faltantes(mock_service, client, admin_token_data):
    """Prueba que la creación falle si faltan parámetros."""
    response = client.post('/api/admin/usuarios', headers=admin_token_data['headers'], json={'username': 'user_incompleto'})

    assert response.status_code == 400

@patch('app.admin.admin_controller.admin_service')
def test_crear_turnos_exito(mock_service, client, admin_token_data):
    """Prueba la creación de turnos de un día con rol de admin (éxito)."""
    mock_service.crear_turnos.return_value = [], []

    response = client.post('/api/admin/turnos/bulk-create', headers=admin_token_data['headers'], query_string={'fecha': '2025-11-20'})

    assert response.status_code == 201

@patch('app.admin.admin_controller.admin_service')
def test_crear_turnos_sin_autorizacion(mock_service, client, client_token_data):
    """Prueba que un usuario no-admin no pueda crear turnos."""
    response = client.post('/api/admin/turnos/bulk-create', headers=client_token_data['headers'], query_string={'fecha': '2025-11-20'})

    assert response.status_code == 403

@patch('app.admin.admin_controller.admin_service')
def test_crear_turnos_fecha_faltante(mock_service, client, admin_token_data):
    """Prueba que la creación de turnos falle si no se envía la fecha."""
    response = client.post('/api/admin/turnos/bulk-create', headers=admin_token_data['headers'])

    assert response.status_code == 400
    assert 'Faltan campos requeridos' in response.get_json()['message']