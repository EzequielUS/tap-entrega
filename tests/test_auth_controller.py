from unittest.mock import patch

@patch('app.auth.auth_controller.auth_service')
def test_login_exitoso(mock_service, client):
    """Prueba el login exitoso de un usuario."""
    mock_service.login.return_value = {
        'token': 'TOKEN_TEST',
        'rol': 'CLIENTE'
    }

    response = client.post('/api/auth/login', json={
        'username': 'cliente_test',
        'password': 'test'
    })
    assert response.status_code == 200
    assert 'token' in response.get_json()
    assert response.get_json()['rol'] == 'CLIENTE'

@patch('app.auth.auth_controller.auth_service')
def test_login_error(mock_service, client):
    """Prueba el login con credenciales inválidas."""
    mock_service.login.return_value = None

    response = client.post('/api/auth/login', json={
        'username': 'cliente_test',
        'password': 'not_test'
    })
    assert response.status_code == 401
    assert 'token' not in response.get_json()

@patch('app.auth.auth_controller.auth_service')
def test_login_parametros_faltantes(mock_service, client):
    """Prueba el login con parámetros faltantes."""
    response = client.post('/api/auth/login', json={
        'username': 'cliente_test'
    })
    assert response.status_code == 400
    assert 'token' not in response.get_json()

@patch('app.auth.auth_controller.auth_service')
def test_protected_route_sin_permiso(mock_service, client):
    """Prueba el acceso a una ruta protegida sin token."""
    response = client.get('/api/auth/test-protected')
    assert response.status_code == 401

@patch('app.auth.auth_controller.auth_service')
def test_protected_route_exito(mock_service, client, client_token_data):
    """Prueba el acceso a una ruta protegida con token válido."""
    response = client.get('/api/auth/test-protected', headers=client_token_data['headers'])
    assert response.status_code == 200