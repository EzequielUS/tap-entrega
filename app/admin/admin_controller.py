from flask import Blueprint, request, jsonify, current_app
from app.auth.auth_required import token_required, roles_required

admin_service = None

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/usuarios', methods=['POST'])
@token_required
@roles_required(['ADMINISTRADOR'])
def crear_usuario():
    """ Crea un nuevo usuario en el sistema. """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    rol = data.get('rol')

    if not all([username, password, rol]):
        current_app.logger.error("Faltan campos requeridos en la creación de usuario.")
        return jsonify({'message': 'Faltan campos requeridos (username, password, rol).'}), 400

    if rol not in ['CLIENTE', 'INSPECTOR', 'ADMINISTRADOR']:
        current_app.logger.error("Rol inválido en la creación de usuario.")
        return jsonify({'message': 'El rol debe ser CLIENTE, INSPECTOR o ADMINISTRADOR.'}), 400

    usuario, error = admin_service.crear_usuario(username, password, rol)
    if error:
        current_app.logger.error(f"Fallo al crear usuario: {error}")
        return jsonify({'message': error}), 409

    return jsonify({'message': f'Usuario "{usuario.username}" creado exitosamente.'}), 201

@admin_bp.route('/usuarios', methods=['GET'])
@token_required
@roles_required(['ADMINISTRADOR'])
def obtener_usuarios():
    """ Devuelve la lista de todos los usuarios. """
    usuarios = admin_service.consultar_usuarios()
    lista_usuarios = [
        {
            'id_usuario': usuario.id_usuario,
            'username': usuario.username,
            'rol': usuario.rol
        } for usuario in usuarios
    ]
    return jsonify(lista_usuarios), 200

@admin_bp.route('/turnos/bulk-create', methods=['POST'])
@token_required
@roles_required(['ADMINISTRADOR'])
def crear_turnos():
    """
    Crea los turnos entre las 9:00 y las 18:00 para una fecha dada.
    Requiere: fecha (YYYY-MM-DD)
    """
    fecha_str = request.args.get('fecha') # Formato: 'YYYY-MM-DD'

    if not fecha_str:
        return jsonify({'message': 'Faltan campos requeridos (fecha).'}), 400

    turnos_creados, error = admin_service.crear_turnos(fecha_str)
    if error:
        return jsonify({'message': error}), 400

    return jsonify({
        'message': f'Se crearon {turnos_creados} turnos para la fecha {fecha_str}.'
    }), 201