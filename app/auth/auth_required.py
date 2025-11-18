from functools import wraps
from flask import request, jsonify, current_app, g
import jwt

def token_required(f):
    """ Decorador que verifica la existencia y validez de un Token Web JSON (JWT) en el header 'Authorization' de la petición."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({
                'message': 'Token de autenticación es requerido. Acceso denegado.'
            }), 401

        try:
            data = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )

            g.current_user = data

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado. Inicie sesión nuevamente.'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'message': 'Token inválido. Acceso denegado.'}), 401
        except Exception as e:
            return jsonify({'message': f'Error de servidor al validar token: {e}'}), 500

        return f(*args, **kwargs)

    return decorated

def roles_required(roles):
    """ Decorador que verifica si el usuario autenticado tiene uno de los roles requeridos. """
    def wrapper(f):
        @wraps(f)
        def decorated_view(*args, **kwargs):
            if 'current_user' in g and g.current_user['rol'] in roles:
                return f(*args, **kwargs)

            return jsonify({
                'message': 'Permisos insuficientes. Rol requerido: ' + ', '.join(roles)
            }), 403
        return decorated_view
    return wrapper