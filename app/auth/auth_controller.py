from flask import Blueprint, request, jsonify, g
from .auth_required import token_required

import bcrypt


auth_service = None

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/test-protected', methods=['GET'])
@token_required
def test_protected_route():
    """ Endpoint de prueba que solo funciona si hay un JWT válido. """
    usuario = g.current_user['username']
    rol = g.current_user['rol']

    return jsonify({
        'message': f'¡Bienvenido, {usuario}!',
        'rol_actual': rol
    }), 200

@auth_bp.route('/hash-creator', methods=['POST'])
def hash_creator():
    """ Endpoint para crear un hash de prueba desde JSON con 'password'. """
    data = request.get_json(silent=True)
    if not data or 'password' not in data:
        return jsonify({'error': 'Se requiere el campo "password"'}), 400
    password = data['password']
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    return jsonify({'hashed_password': hashed}), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    """ Endpoint para autenticar un usuario y devolver un token JWT. """
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Faltan credenciales (username/password)'}), 400

    usuario = data['username']
    password = data['password']

    global auth_service
    auth_result = auth_service.login(usuario, password)
    if auth_result:
        return jsonify({
            'message': 'Autenticación exitosa',
            'token': auth_result['token'],
            'rol': auth_result['rol']
        }), 200
    else:
        return jsonify({'message': 'Usuario o contraseña incorrectos'}), 401
