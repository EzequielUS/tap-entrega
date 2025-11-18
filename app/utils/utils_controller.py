from flask import Blueprint, jsonify, current_app

utils_bp = Blueprint('utils', __name__, url_prefix='/api')

@utils_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint para que Docker Compose sepa que la aplicación está viva."""
    current_app.logger.info("Recepción de mensaje exitoso!")
    return jsonify({
        'status': 'ok',
        'service': 'vehicles-api-service',
        'version': '1.0'
    }), 200