from unittest.mock import MagicMock
from app.admin.admin_service import AdminService
from app.models import Usuario

def test_crear_usuario_exito():
    """Prueba la creación de un usuario con rol de admin (éxito)."""
    # Mocks para los DAOs
    mock_usuario_dao = MagicMock()
    mock_turno_dao = MagicMock()

    mock_usuario_dao.obtener_por_username.return_value = None
    mock_usuario_dao.crear.return_value = 123

    service = AdminService(mock_usuario_dao, mock_turno_dao)
    nuevo_usuario, error = service.crear_usuario('nuevo_user', 'password123', 'CLIENTE')

    assert error is None
    assert nuevo_usuario is not None
    assert nuevo_usuario.username == 'nuevo_user'
    assert nuevo_usuario.id_usuario == 123
    mock_usuario_dao.crear.assert_called_once()

def test_crear_usuario_ya_existente():
    """Prueba que la creación falle si el usuario ya existe."""
    mock_usuario_dao = MagicMock()
    mock_turno_dao = MagicMock()

    # Simular que el DAO encuentra un usuario con ese nombre
    mock_usuario_dao.obtener_por_username.return_value = Usuario(id_usuario=1, username='user_existente', password_hash='...', rol='CLIENTE')

    service = AdminService(mock_usuario_dao, mock_turno_dao)
    nuevo_usuario, error = service.crear_usuario('user_existente', 'password123', 'CLIENTE')

    assert nuevo_usuario is None
    assert error == "El usuario 'user_existente' ya existe."
    mock_usuario_dao.crear.assert_not_called()

def test_crear_turnos_exito():
    """Prueba la creación automática de turnos para un día."""
    mock_usuario_dao = MagicMock()
    mock_turno_dao = MagicMock()

    # Simular que el DAO de turnos reporta 18 filas insertadas
    mock_turno_dao.crear_varios.return_value = 18

    service = AdminService(mock_usuario_dao, mock_turno_dao)
    turnos_creados, error = service.crear_turnos('2025-12-25')

    assert error is None
    assert turnos_creados == 18
    mock_turno_dao.crear_varios.assert_called_once()
    # Verificar que se generaron 18 turnos (de 9:00 a 17:30)
    assert len(mock_turno_dao.crear_varios.call_args[0][0]) == 18

def test_crear_turnos_fecha_invalida():
    """Prueba que la creación de turnos falle si la fecha es inválida."""
    mock_usuario_dao = MagicMock()
    mock_turno_dao = MagicMock()

    service = AdminService(mock_usuario_dao, mock_turno_dao)
    turnos_creados, error = service.crear_turnos('25-12-2025') # Formato incorrecto

    assert turnos_creados is None
    mock_turno_dao.crear_varios.assert_not_called()