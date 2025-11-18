from unittest.mock import patch

# Datos de prueba para simplificar
FECHA_OK = "2025-11-18"
TOKEN_CLIENTE = "TOKEN_TEST_CLIENTE"
TOKEN_INSPECTOR = "TOKEN_TEST_INSPECTOR"

ID_TURNO_SLOT = 50
MATRICULA_VEHICULO = 'XYZ-999'

@patch('app.turnos.turno_controller.turno_service')
def test_consultar_disponibilidad_ok(mock_service, client, client_token_data):
    """Prueba la consulta de disponibilidad de turnos (éxito)."""
    mock_service.consultar_disponibilidad.return_value = ([
        {'id_turno': 1, 'fecha': '2025-11-18 09:00:00', 'estado': 'LIBRE'}
    ], None)

    response = client.get(f'/api/turnos/disponibilidad?fecha={FECHA_OK}', headers=client_token_data['headers'])

    assert response.status_code == 200
    assert len(response.get_json()['disponibles']) == 1
    mock_service.consultar_disponibilidad.assert_called_once_with(FECHA_OK)

@patch('app.turnos.turno_controller.turno_service')
def test_consultar_disponibilidad_parametros_faltantes(mock_service, client, client_token_data):
    """Prueba que la consulta de disponibilidad falle si faltan parámetros."""
    response = client.get('/api/turnos/disponibilidad', headers=client_token_data['headers'])

    assert response.status_code == 400
    assert 'Se requiere el parámetro "fecha"' in response.get_json()['message']

@patch('app.turnos.turno_controller.turno_service')
def test_reservar_turno_exito(mock_service, client, client_token_data):
    """Prueba la reserva de un turno (éxito)."""

    resultado_mock = {
        'id_turno': ID_TURNO_SLOT,
        'estado': 'RESERVADO',
        'matricula': MATRICULA_VEHICULO
    }
    mock_service.reservar_turno.return_value = (resultado_mock, None)

    payload = {
        'matricula': MATRICULA_VEHICULO,
        'id_marca': 1,
        'anio': 2020,
        'id_turno': ID_TURNO_SLOT
    }

    response = client.post('/api/turnos/reservar',
                        headers=client_token_data['headers'],
                        json=payload)

    assert response.status_code == 201
    assert 'Turno reservado exitosamente' in response.get_json()['message']

    mock_service.reservar_turno.assert_called_once_with(
        payload['matricula'],
        payload['id_marca'],
        payload['anio'],
        payload['id_turno']
    )

@patch('app.turnos.turno_controller.turno_service')
def test_reservar_turno_sin_permiso(mock_service, client, inspector_token_data):
    """Prueba que un inspector no pueda reservar un turno."""
    payload = {
        'matricula': MATRICULA_VEHICULO,
        'id_marca': 1,
        'anio': 2020,
        'id_turno': ID_TURNO_SLOT
    }

    response = client.post('/api/turnos/reservar', headers=inspector_token_data['headers'], json=payload)
    assert response.status_code == 403

@patch('app.turnos.turno_controller.turno_service')
def test_consultar_turno_exito(mock_service, client, client_token_data):
    """Prueba la consulta de un turno por ID (éxito)."""
    ID_TURNO = 10

    mock_service.consultar_turno.return_value = ({
        'id_turno': ID_TURNO,
        'estado': 'RESERVADO',
        'matricula': MATRICULA_VEHICULO
    }, None)

    response = client.get(f'/api/turnos/{ID_TURNO}/consultar', headers=client_token_data['headers'])

    assert response.status_code == 200
    assert response.get_json()['turno']['id_turno'] == ID_TURNO

    mock_service.consultar_turno.assert_called_once_with(ID_TURNO)

@patch('app.turnos.turno_controller.turno_service')
def test_consultar_turno_no_encontrado(mock_service, client, client_token_data):
    """Prueba la consulta de un turno por ID que no existe."""
    ID_TURNO = 999

    mock_service.consultar_turno.return_value = (None, "Turno no encontrado.")
    response = client.get(f'/api/turnos/{ID_TURNO}/consultar', headers=client_token_data['headers'])

    assert response.status_code == 404
    assert 'Turno no encontrado' in response.get_json()['message']

    mock_service.consultar_turno.assert_called_once_with(ID_TURNO)

@patch('app.turnos.turno_controller.turno_service')
def test_consultar_turnos_pendientes_exito(mock_service, client, inspector_token_data):
    mock_service.consultar_turnos_pendientes.return_value = ([
        {'id_turno': 1, 'estado': 'RESERVADO'},
        {'id_turno': 2, 'estado': 'RESERVADO'}
    ], None)

    response = client.get('/api/turnos/pendientes', headers=inspector_token_data['headers'])

    assert response.status_code == 200
    assert len(response.get_json()['turnos_pendientes']) == 2
    mock_service.consultar_turnos_pendientes.assert_called_once()

@patch('app.turnos.turno_controller.turno_service')
def test_consultar_turnos_pendientes_vacio(mock_service, client, inspector_token_data):
    """Prueba la consulta de turnos pendientes cuando no hay ninguno."""
    mock_service.consultar_turnos_pendientes.return_value = ([], None)

    response = client.get('/api/turnos/pendientes', headers=inspector_token_data['headers'])

    assert response.status_code == 200
    assert len(response.get_json()['turnos_pendientes']) == 0
    mock_service.consultar_turnos_pendientes.assert_called_once()

@patch('app.turnos.turno_controller.turno_service')
def test_consultar_turnos_pendientes_sin_permiso(mock_service, client, client_token_data):
    """Prueba que un cliente no pueda consultar turnos pendientes."""
    response = client.get('/api/turnos/pendientes', headers=client_token_data['headers'])
    assert response.status_code == 403

@patch('app.turnos.turno_controller.turno_service')
def test_finalizar_turno_exito(mock_service, client, inspector_token_data):
    """Prueba la finalización de un turno (éxito)."""
    ID_TURNO = 10

    mock_service.finalizar_turno_inspeccion.return_value = ({
        'id_turno': ID_TURNO,
        'estado': 'FINALIZADO',
        'resultado': {}
    }, None)

    detalles = [{'id_control': i, 'calificacion': 10, 'observaciones': ''} for i in range(1, 9)]

    response = client.post(f'/api/turnos/{ID_TURNO}/finalizar',
                            headers=inspector_token_data['headers'],
                            json={'detalles_control': detalles})

    assert response.status_code == 200

@patch('app.turnos.turno_controller.turno_service')
def test_finalizar_turno_error(mock_service, client, inspector_token_data):
    """Prueba la finalización de un turno con error por datos inválidos."""
    ID_TURNO = 10
    detalles = [{'id_control': i, 'calificacion': 10, 'observaciones': ''} for i in range(1, 8)]

    response = client.post(f'/api/turnos/{ID_TURNO}/finalizar',
                        headers=inspector_token_data['headers'],
                        json={'detalles_control': detalles})

    assert response.status_code == 400

def test_finalizar_turno_sin_autorizacion(client, client_token_data):
    """Prueba que un cliente no pueda finalizar un turno."""
    ID_TURNO = 10
    detalles = [{'id_control': i, 'calificacion': 10, 'observaciones': ''} for i in range(1, 9)]

    response = client.post(f'/api/turnos/{ID_TURNO}/finalizar',
                           headers=client_token_data['headers'],
                           json={'detalles_control': detalles})

    assert response.status_code == 403
