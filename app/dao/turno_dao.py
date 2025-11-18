# app/dao/turno_dao.py

from ..db_connection import DBConnection
from ..models import Turno
from datetime import datetime # Necesaria para manejar DATETIME

class TurnoDAO:

    def crear(self, turno: Turno):
        """ Inserta un nuevo turno en la DB y retorna su ID. """
        query = """
            INSERT INTO Turnos (matricula, fecha, estado)
            VALUES (%s, %s, %s)
        """
        if not isinstance(turno.fecha, datetime):
            raise TypeError("El campo 'fecha' debe ser un objeto datetime.")

        params = (
            turno.matricula,
            turno.fecha,
            turno.estado
        )

        try:
            with DBConnection() as db:
                db.cursor.execute(query, params)
                db.connection.commit()
                return db.cursor.lastrowid
        except Exception as e:
            print(f"Error al crear turno en DB: {e}")
            return None

    def crear_varios(self, turnos: list[Turno]):
        """ Inserta una lista de turnos en una única transacción. """
        query = "INSERT INTO Turnos (fecha, estado) VALUES (%s, %s)"

        # Prepara una lista de tuplas con los datos de cada turno
        params_list = [(t.fecha, t.estado) for t in turnos]

        try:
            with DBConnection() as db:
                db.cursor.executemany(query, params_list)
                db.connection.commit()
                return db.cursor.rowcount
        except Exception as e:
            print(f"Error al crear varios turnos en DB: {e}")
            return None

    def obtener_por_id(self, id_turno: int):
        """ Busca y devuelve un objeto Turno por su ID. """
        query = """
            SELECT id_turno, matricula, fecha, estado, id_resultado
            FROM Turnos
            WHERE id_turno = %s
        """

        try:
            with DBConnection() as db:
                db.cursor.execute(query, (id_turno,))
                data = db.cursor.fetchone()

            if data:
                return Turno(
                    id_turno=data['id_turno'],
                    matricula=data['matricula'],
                    fecha=data['fecha'],
                    estado=data['estado'],
                    id_resultado=data['id_resultado']
                )
            return None

        except Exception as e:
            print(f"Error al obtener turno por ID: {e}")
            return None

    def obtener_disponibles_por_fecha(self, fecha_consulta):
        """ Devuelve una lista de objetos Turno en estado 'LIBRE' para la fecha dada."""
        query = """
            SELECT id_turno, matricula, fecha, estado, id_resultado
            FROM Turnos
            WHERE DATE(fecha) = %s AND estado = 'LIBRE'
            ORDER BY fecha ASC
        """
        try:
            with DBConnection() as db:
                db.cursor.execute(query, (fecha_consulta,))
                data_list = db.cursor.fetchall()

            return [Turno(**data) for data in data_list]
        except Exception as e:
            print(f"Error al obtener turnos disponibles: {e}")
            return []

    def obtener_pendientes(self):
        """ Devuelve una lista de objetos Turno en estado 'RESERVADO'. """
        query = """
            SELECT id_turno, matricula, fecha, estado, id_resultado
            FROM Turnos
            WHERE estado = 'RESERVADO'
            ORDER BY fecha ASC
        """
        try:
            with DBConnection() as db:
                db.cursor.execute(query)
                data_list = db.cursor.fetchall()

            return [Turno(**data) for data in data_list]
        except Exception as e:
            print(f"Error al obtener turnos pendientes: {e}")
            return []

    def actualizar_a_reservado(self, id_turno: int, matricula: str):
        """Actualiza el slot LIBRE con la matrícula y cambia el estado a 'RESERVADO'."""
        query = """
            UPDATE Turnos
            SET matricula = %s, estado = 'RESERVADO'
            WHERE id_turno = %s AND estado = 'LIBRE'
        """
        try:
            with DBConnection() as db:
                db.cursor.execute(query, (matricula, id_turno))
                db.connection.commit()
                if db.cursor.rowcount > 0:
                    return self.obtener_por_id(id_turno)
                return None
        except Exception as e:
            print(f"Error al actualizar a reservado: {e}")
            return None
