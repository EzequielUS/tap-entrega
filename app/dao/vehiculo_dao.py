# app/dao/vehiculo_dao.py
from flask import current_app
from ..db_connection import DBConnection
from ..models import Vehiculo

class VehiculoDAO:
    def crear(self, vehiculo: Vehiculo):
        """ Crea un nuevo vehículo en la base de datos."""
        if self.obtener_por_matricula(vehiculo.matricula):
            current_app.logger.warning(f"Vehículo con matrícula {vehiculo.matricula} ya existe. Saltando inserción.")
            return True

        query = """
            INSERT INTO Vehiculos (matricula, id_marca, anio)
            VALUES (%s, %s, %s)
        """
        params = (vehiculo.matricula, vehiculo.id_marca, vehiculo.anio)

        try:
            with DBConnection() as db:
                db.cursor.execute(query, params)
                db.connection.commit()
                return True
        except Exception as e:
            current_app.logger.error(f"Error al crear vehículo en DB: {e}")
            return False

    def obtener_por_matricula(self, matricula: str):
        """ Busca y devuelve un objeto Vehiculo por su matrícula."""
        query = "SELECT matricula, id_marca, anio FROM Vehiculos WHERE matricula = %s"

        try:
            with DBConnection() as db:
                db.cursor.execute(query, (matricula,))
                data = db.cursor.fetchone()

            if data:
                return Vehiculo(
                    matricula=data['matricula'],
                    id_marca=data['id_marca'],
                    anio=data['anio']
                )
            return None

        except Exception as e:
            current_app.logger.error(f"Error al obtener vehículo en DB: {e}")
            return None