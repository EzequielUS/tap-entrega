import bcrypt
from datetime import time, timedelta
from datetime import datetime
from ..dao.usuario_dao import UsuarioDAO
from ..dao.turno_dao import TurnoDAO
from ..models import Usuario, Turno

class AdminService:
    def __init__(self, usuario_dao: UsuarioDAO, turno_dao: TurnoDAO):
        self.usuario_dao = usuario_dao
        self.turno_dao = turno_dao

    def crear_usuario(self, username, password, rol):
        """ Hashea la contraseña y crea un nuevo usuario. """

        if self.usuario_dao.obtener_por_username(username):
            return None, f"El usuario '{username}' ya existe."

        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        nuevo_usuario = Usuario(
            username=username,
            password_hash=hashed_pw,
            rol=rol
        )

        id_usuario = self.usuario_dao.crear(nuevo_usuario)
        if id_usuario:
            nuevo_usuario.id_usuario = id_usuario
            return nuevo_usuario, None

        return None, "Error al crear el usuario en la base de datos."

    def consultar_usuarios(self):
        """ Devuelve la lista de todos los usuarios. """
        usuarios = self.usuario_dao.obtener_todos()
        return usuarios

    def crear_turnos(self, fecha_str):
        """ Crea múltiples turnos para una fecha y lista de horas dadas. """
        try:
            fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return None, "Formato de fecha inválido. Usar YYYY-MM-DD."

        turnos_a_crear = []
        hora_inicio = time(9, 0)
        hora_fin = time(18, 0)
        intervalo = timedelta(minutes=30)

        datetime_actual = datetime.combine(fecha_obj, hora_inicio)
        datetime_fin = datetime.combine(fecha_obj, hora_fin)

        while datetime_actual < datetime_fin:
            turno = Turno(
                matricula=None,
                fecha=datetime_actual,
                estado='LIBRE'
            )
            turnos_a_crear.append(turno)
            datetime_actual += intervalo

        if not turnos_a_crear:
            return 0, None

        rows_affected = self.turno_dao.crear_varios(turnos_a_crear)
        if rows_affected is not None:
            return rows_affected, None

        return None, "Error al insertar los turnos en la base de datos."