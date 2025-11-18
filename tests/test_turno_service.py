# tests/test_turno_service.py
from unittest.mock import MagicMock
from app.turnos.turno_service import TurnoService


def test_consultar_disponibilidad_ok():
    """Prueba la consulta de disponibilidad de turnos (éxito)."""
    # Configurar el mock del DAO
    turno_dao = MagicMock()
    vehiculo_dao = MagicMock()
    resultado_dao = MagicMock()

    turno1 = MagicMock()
    turno2 = MagicMock()

    turno1.to_dict.return_value = {'id_turno': 1, 'estado': 'LIBRE', 'fecha': '2024-06-15'}
    turno2.to_dict.return_value = {'id_turno': 2, 'estado': 'LIBRE', 'fecha': '2024-06-15'}
    turno_dao.obtener_disponibles_por_fecha.return_value = [turno1, turno2]

    service = TurnoService(turno_dao, vehiculo_dao, resultado_dao)
    resultado, _ = service.consultar_disponibilidad('2024-06-15')

    assert len(resultado) == 2
    assert resultado[0]['id_turno'] == 1
    assert resultado[1]['id_turno'] == 2

def test_consultar_disponibilidad_formato_fecha_invalido():
    """Prueba que la consulta de disponibilidad falle si la fecha es inválida."""
    # Configurar el mock no es necesario aquí ya que no se llegará a llamar al DAO

    turno_dao = MagicMock()
    vehiculo_dao = MagicMock()
    resultado_dao = MagicMock()

    service = TurnoService(turno_dao, vehiculo_dao, resultado_dao)
    resultado, _ = service.consultar_disponibilidad('2024-13-01')  # Fecha inválida

    assert resultado is None

def test_reservar_turno_ok():
    """Prueba la reserva exitosa de un turno."""
    turno_dao = MagicMock()
    vehiculo_dao = MagicMock()
    resultado_dao = MagicMock()

    vehiculo_dao.crear.return_value = None  # Simula creación exitosa

    turno_previo = MagicMock()
    turno_previo.estado = 'LIBRE'
    turno_previo.to_dict.return_value = {'id_turno': 1, 'estado': 'RESERVADO', 'matricula': 'ABC123'}

    turno_post = MagicMock()
    turno_post.estado = 'RESERVADO'
    turno_post.to_dict.return_value = {'id_turno': 1, 'estado': 'RESERVADO', 'matricula': 'ABC123'}

    turno_dao.obtener_por_id.return_value = turno_previo
    turno_dao.actualizar_a_reservado.return_value = turno_post

    service = TurnoService(turno_dao, vehiculo_dao, resultado_dao)
    resultado, _ = service.reservar_turno('ABC123', 1, 2020, 1)

    assert resultado['estado'] == 'RESERVADO'
    assert resultado['matricula'] == 'ABC123'

def test_reservar_turno_no_encontrado():
    """Prueba que la reserva falle si el turno no existe."""
    turno_dao = MagicMock()
    vehiculo_dao = MagicMock()
    resultado_dao = MagicMock()

    vehiculo_dao.crear.return_value = None  # Simula creación exitosa
    turno_dao.obtener_por_id.return_value = None  # Simula que no se encuentra el turno

    service = TurnoService(turno_dao, vehiculo_dao, resultado_dao)
    resultado, mensaje = service.reservar_turno('ABC123', 1, 2020, 999)  # ID de turno inexistente

    assert resultado is None
    assert mensaje == "ID de turno no encontrado."

def test_reservar_turno_no_libre():
    """Prueba que la reserva falle si el turno no está libre."""
    turno_dao = MagicMock()
    vehiculo_dao = MagicMock()
    resultado_dao = MagicMock()

    vehiculo_dao.crear.return_value = None  # Simula creación exitosa

    turno_previo = MagicMock()
    turno_previo.estado = 'RESERVADO'  # Ya reservado

    turno_dao.obtener_por_id.return_value = turno_previo

    service = TurnoService(turno_dao, vehiculo_dao, resultado_dao)
    resultado, mensaje = service.reservar_turno('ABC123', 1, 2020, 1)

    assert resultado is None
    assert mensaje == "El turno 1 ya está RESERVADO."

def test_reservar_turno_error_actualizacion():
    """Prueba que la reserva falle si hay un error al actualizar el turno."""
    turno_dao = MagicMock()
    vehiculo_dao = MagicMock()
    resultado_dao = MagicMock()

    vehiculo_dao.crear.return_value = None  # Simula creación exitosa

    turno_previo = MagicMock()
    turno_previo.estado = 'LIBRE'

    turno_dao.obtener_por_id.return_value = turno_previo
    turno_dao.actualizar_a_reservado.return_value = None  # Simula error en actualización

    service = TurnoService(turno_dao, vehiculo_dao, resultado_dao)
    resultado, mensaje = service.reservar_turno('ABC123', 1, 2020, 1)

    assert resultado is None
    assert mensaje == "Error al actualizar el estado del turno."

def test_consultar_turno_finalizado():
    """Prueba la consulta de un turno finalizado con resultado de inspección."""
    turno_dao = MagicMock()
    vehiculo_dao = MagicMock()
    resultado_dao = MagicMock()

    turno = MagicMock()
    turno.estado = 'FINALIZADO'
    turno.id_resultado = 10
    turno.to_dict.return_value = {'id_turno': 1, 'estado': 'FINALIZADO'}

    resultado_completo = {'detalles': 'Inspección completa'}
    resultado_dao.obtener_resultado_completo.return_value = resultado_completo

    turno_dao.obtener_por_id.return_value = turno

    service = TurnoService(turno_dao, vehiculo_dao, resultado_dao)
    resultado, _ = service.consultar_turno(1)

    assert resultado['id_turno'] == 1
    assert resultado['resultado_inspeccion'] == resultado_completo

def test_consultar_turno_no_finalizado():
    """Prueba la consulta de un turno que no está finalizado."""
    turno_dao = MagicMock()
    vehiculo_dao = MagicMock()
    resultado_dao = MagicMock()

    turno = MagicMock()
    turno.estado = 'RESERVADO'
    turno.id_resultado = None
    turno.to_dict.return_value = {'id_turno': 1, 'estado': 'RESERVADO'}

    turno_dao.obtener_por_id.return_value = turno

    service = TurnoService(turno_dao, vehiculo_dao, resultado_dao)
    resultado, _ = service.consultar_turno(1)

    assert resultado['id_turno'] == 1
    assert resultado['resultado_inspeccion'] is None

def test_consultar_turno_no_encontrado():
    """Prueba que la consulta de un turno falle si no se encuentra."""
    turno_dao = MagicMock()
    vehiculo_dao = MagicMock()
    resultado_dao = MagicMock()

    turno_dao.obtener_por_id.return_value = None

    service = TurnoService(turno_dao, vehiculo_dao, resultado_dao)
    resultado, mensaje = service.consultar_turno(999)

    assert resultado is None
    assert mensaje == "Turno no encontrado."

def test_consultar_turnos_pendientes():
    turno_dao = MagicMock()
    vehiculo_dao = MagicMock()
    resultado_dao = MagicMock()

    turno1 = MagicMock()
    turno2 = MagicMock()

    turno1.to_dict.return_value = {'id_turno': 1, 'estado': 'RESERVADO'}
    turno2.to_dict.return_value = {'id_turno': 2, 'estado': 'RESERVADO'}

    turno_dao.obtener_pendientes.return_value = [turno1, turno2]

    service = TurnoService(turno_dao, vehiculo_dao, resultado_dao)
    resultado, _ = service.consultar_turnos_pendientes()

    assert len(resultado) == 2
    assert resultado[0]['id_turno'] == 1
    assert resultado[1]['id_turno'] == 2

def test_consultar_turnos_pendientes_vacio():
    """Prueba la consulta de turnos pendientes cuando no hay ninguno."""
    turno_dao = MagicMock()
    vehiculo_dao = MagicMock()
    resultado_dao = MagicMock()

    turno_dao.obtener_pendientes.return_value = []

    service = TurnoService(turno_dao, vehiculo_dao, resultado_dao)
    resultado, _ = service.consultar_turnos_pendientes()

    assert len(resultado) == 0

def test_finalizar_turno_inspeccion_ok():
    """Prueba la finalización exitosa de un turno de inspección."""
    turno_dao = MagicMock()
    vehiculo_dao = MagicMock()
    resultado_dao = MagicMock()

    turno = MagicMock()
    turno.estado = 'RESERVADO'

    turno_dao.obtener_por_id.return_value = turno
    resultado_dao.crear_resultado_inspeccion.return_value = 20
    turno_dao.actualizar_a_finalizado.return_value = MagicMock()

    service = TurnoService(turno_dao, vehiculo_dao, resultado_dao)
    detalles_control = [
        {'id_control': 1, 'calificacion': 8, 'observacion': 'OK'},
        {'id_control': 2, 'calificacion': 7, 'observacion': 'OK'},
        {'id_control': 3, 'calificacion': 9, 'observacion': 'OK'},
        {'id_control': 4, 'calificacion': 6, 'observacion': 'OK'},
        {'id_control': 5, 'calificacion': 8, 'observacion': 'OK'},
        {'id_control': 6, 'calificacion': 8, 'observacion': 'OK'},
        {'id_control': 7, 'calificacion': 7, 'observacion': 'OK'},
        {'id_control': 8, 'calificacion': 5, 'observacion': 'OK'},
    ]

    resultado, _ = service.finalizar_turno_inspeccion(1, detalles_control)

    assert resultado is not None
    assert resultado['id_turno'] == 1
    assert resultado['resultado'] in ['SEGURO', 'SEGURO CON ADVERTENCIA']

def test_finalizar_turno_inspeccion_no_encontrado():
    turno_dao = MagicMock()
    vehiculo_dao = MagicMock()
    resultado_dao = MagicMock()

    turno_dao.obtener_por_id.return_value = None

    service = TurnoService(turno_dao, vehiculo_dao, resultado_dao)
    detalles_control = []

    resultado, mensaje = service.finalizar_turno_inspeccion(999, detalles_control)

    assert resultado is None
    assert mensaje == "Turno no encontrado o no está listo para ser finalizado."

def test_determinar_resultado_final():
    """Prueba la lógica de determinación del resultado final de la inspección."""
    turno_dao = MagicMock()
    vehiculo_dao = MagicMock()
    resultado_dao = MagicMock()

    service = TurnoService(turno_dao, vehiculo_dao, resultado_dao)

    assert service._determinar_resultado_final(30, False) == 'RECHEQUEAR'
    assert service._determinar_resultado_final(50, True) == 'RECHEQUEAR'
    assert service._determinar_resultado_final(85, False) == 'SEGURO'
    assert service._determinar_resultado_final(70, False) == 'SEGURO CON ADVERTENCIA'

def test_procesar_detalles_inspeccion():
    """Prueba el procesamiento de los detalles de inspección."""
    turno_dao = MagicMock()
    vehiculo_dao = MagicMock()
    resultado_dao = MagicMock()

    service = TurnoService(turno_dao, vehiculo_dao, resultado_dao)

    detalles_control = [
        {'id_control': 1, 'calificacion': 8, 'observaciones': 'OK'},
        {'id_control': 2, 'calificacion': 4, 'observaciones': 'Falla crítica'},
        {'id_control': 3, 'calificacion': 7, 'observaciones': 'OK'},
    ]

    puntaje_total, falla_critica, detalles_obj, error = service._procesar_detalles_inspeccion(detalles_control)

    assert puntaje_total == 19
    assert falla_critica is True
    assert len(detalles_obj) == 3
    assert error is None