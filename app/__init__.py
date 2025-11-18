from flask import Flask
from .config import Config

from .logging_config import configure_logging

# DAOs
from .dao.usuario_dao import UsuarioDAO
from .dao.turno_dao import TurnoDAO
from .dao.vehiculo_dao import VehiculoDAO
from .dao.resultado_dao import ResultadoDAO

# Servicios
from .auth.auth_service import AuthService
from .turnos.turno_service import TurnoService
from .admin.admin_service import AdminService

# Controladores
from .auth import auth_controller
from .turnos import turno_controller
from .utils import utils_controller
from .admin import admin_controller

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    configure_logging(app)

    usuario_dao = UsuarioDAO()
    turno_dao = TurnoDAO()
    vehiculo_dao = VehiculoDAO()
    resultado_dao = ResultadoDAO()

    auth_service_instance = AuthService(usuario_dao)
    turno_service_instance = TurnoService(turno_dao, vehiculo_dao, resultado_dao)
    admin_service_instance = AdminService(usuario_dao, turno_dao)

    auth_controller.auth_service = auth_service_instance
    turno_controller.turno_service = turno_service_instance
    admin_controller.admin_service = admin_service_instance

    app.register_blueprint(auth_controller.auth_bp)
    app.register_blueprint(turno_controller.turno_bp)
    app.register_blueprint(utils_controller.utils_bp)
    app.register_blueprint(admin_controller.admin_bp)

    return app
