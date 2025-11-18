# app/turnos/turno_controller.py
from flask import Blueprint, jsonify, request, current_app
from app.auth.auth_required import token_required, roles_required

turno_service = None

turno_bp = Blueprint('turnos', __name__, url_prefix='/api/turnos')

@turno_bp.route('/disponibilidad', methods=['GET'])
@token_required
@roles_required(['CLIENTE', 'INSPECTOR', 'ADMINISTRADOR'])
def consultar_disponibilidad():
    """ Ruta para consultar los slots libres en una fecha dada. """
    current_app.logger.info("Consulta de disponibilidad de turnos iniciada.")
    fecha_str = request.args.get('fecha') # Formato: 'YYYY-MM-DD'
    if not fecha_str:
        return jsonify({'message': 'Se requiere el parámetro "fecha" (YYYY-MM-DD)'}), 400

    disponibles, error = turno_service.consultar_disponibilidad(fecha_str)

    if error:
        current_app.logger.error(f"Error al consultar disponibilidad: {error}")
        return jsonify({'message': error}), 400

    current_app.logger.info(f"Disponibilidad consultada exitosamente para {fecha_str}.")
    return jsonify({'disponibles': disponibles}), 200

@turno_bp.route('/reservar', methods=['POST'])
@token_required
@roles_required(['CLIENTE', 'ADMINISTRADOR'])
def reservar_turno():
    """ Ruta para que un cliente solicite un turno libre."""
    current_app.logger.info("Solicitud de reserva de turno recibida.")

    data = request.get_json()

    id_turno = data.get('id_turno')
    matricula = data.get('matricula')
    id_marca = data.get('id_marca')
    anio = data.get('anio')

    if not all([matricula, id_marca, anio, id_turno]):
        current_app.logger.error("Faltan campos requeridos en la solicitud de reserva.")
        return jsonify({'message': 'Faltan campos requeridos (matricula, id_marca, anio, id_turno).'}), 400

    turno, error = turno_service.reservar_turno(matricula, id_marca, anio, id_turno)
    if error:
        current_app.logger.error(f"Fallo al reservar turno: {error}")
        return jsonify({'message': error}), 409

    current_app.logger.info(f"Turno {id_turno} reservado exitosamente para vehículo {matricula}.")
    return jsonify({
        'message': 'Turno reservado exitosamente.',
        'turno': turno
    }), 201

@turno_bp.route('/<int:id_turno>/consultar', methods=['GET'])
@token_required
@roles_required(['CLIENTE', 'INSPECTOR', 'ADMINISTRADOR'])
def consultar_turno(id_turno):
    """ Ruta para consultar los detalles de un turno específico."""
    current_app.logger.info(f"Consulta de turno iniciada para ID: {id_turno}")
    turno, error = turno_service.consultar_turno(id_turno)
    if error:
        current_app.logger.error(f"Error al consultar turno {id_turno}: {error}")
        return jsonify({'message': error}), 404

    current_app.logger.info(f"Turno {id_turno} consultado exitosamente.")
    return jsonify({'turno': turno}), 200

@turno_bp.route('/pendientes', methods=['GET'])
@token_required
@roles_required(['INSPECTOR', 'ADMINISTRADOR'])
def consultar_turnos_pendientes():
    """ Ruta para consultar todos los turnos pendientes. """
    current_app.logger.info("Consulta de turnos pendientes iniciada.")
    turnos_pendientes, error = turno_service.consultar_turnos_pendientes()
    if error:
        current_app.logger.error(f"Error al consultar turnos pendientes: {error}")
        return jsonify({'message': error}), 400

    current_app.logger.info("Consulta de turnos pendientes finalizada.")
    return jsonify({'turnos_pendientes': turnos_pendientes}), 200

@turno_bp.route('/<int:id_turno>/finalizar', methods=['POST'])
@token_required
@roles_required(['INSPECTOR', 'ADMINISTRADOR'])
def finalizar_turno(id_turno):
    """ Ruta para que el Inspector cargue los resultados de la inspección. """
    current_app.logger.info(f"Finalización de turno iniciada para ID: {id_turno}")

    data = request.get_json()
    detalles_control = data.get('detalles_control')

    if not detalles_control or len(detalles_control) != 8:
        current_app.logger.error("Faltan detalles de control en la solicitud.")
        return jsonify({
            'message': 'Se requiere una lista de 8 detalles de control con calificación.'
        }), 400

    resultado_final, error = turno_service.finalizar_turno_inspeccion(id_turno, detalles_control)
    if error:
        current_app.logger.error(f"Fallo al finalizar turno {id_turno}: {error}")
        return jsonify({'message': error}), 409

    current_app.logger.info(f"Turno {id_turno} finalizado exitosamente con resultado: {resultado_final['resultado']}.")
    return jsonify({
        'message': f"Inspección finalizada. Resultado: {resultado_final['resultado']}",
        'id_turno': resultado_final['id_turno']
    }), 200