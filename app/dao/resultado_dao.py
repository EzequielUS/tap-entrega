from flask import current_app

from ..db_connection import DBConnection
from ..models import Resultado, ResultadoPorControl, Turno

class ResultadoDAO:

    def registrar_resultado_inspeccion(self, turno: Turno, resultado: Resultado, detalles_control: list[ResultadoPorControl]):
        """ Registra la inspección completa en una sola transacción. """

        try:
            with DBConnection() as db:
                query_resultado = """
                    INSERT INTO Resultados (resultado, puntaje_total, observaciones)
                    VALUES (%s, %s, %s)
                """
                params_resultado = (resultado.resultado, resultado.puntaje_total, resultado.observaciones)
                db.cursor.execute(query_resultado, params_resultado)

                id_resultado = db.cursor.lastrowid

                query_detalle = """
                    INSERT INTO ResultadosPorControl (id_resultado, id_control, calificacion, observaciones)
                    VALUES (%s, %s, %s, %s)
                """

                detalles_a_insertar = []
                for detalle in detalles_control:
                    detalles_a_insertar.append((
                        id_resultado,
                        detalle.id_control,
                        detalle.calificacion,
                        detalle.observaciones
                    ))

                db.cursor.executemany(query_detalle, detalles_a_insertar)

                query_turno = """
                    UPDATE Turnos
                    SET id_resultado = %s, estado = 'FINALIZADO'
                    WHERE id_turno = %s
                """
                params_turno = (id_resultado, turno.id_turno)
                db.cursor.execute(query_turno, params_turno)

                db.connection.commit()
                return id_resultado

        except Exception as e:
            current_app.logger.error(f"Error al registrar resultado de inspección en DB: {e}")
            return None

    def obtener_resultado_completo(self, id_resultado: int):
        """ Obtiene la cabecera del resultado y todos sus detalles (ResultadosPorControl). """
        try:
            with DBConnection() as db:
                query_cabecera = """
                    SELECT id_resultado, resultado, puntaje_total, observaciones
                    FROM Resultados WHERE id_resultado = %s
                """
                db.cursor.execute(query_cabecera, (id_resultado,))
                cabecera_data = db.cursor.fetchone()

                if not cabecera_data:
                    return None

                query_detalles = """
                    SELECT id_control, calificacion, observaciones
                    FROM ResultadosPorControl WHERE id_resultado = %s
                """
                db.cursor.execute(query_detalles, (id_resultado,))
                detalles_data = db.cursor.fetchall()

            resultado_completo = Resultado(**cabecera_data).to_dict()
            resultado_completo['detalles_control'] = [dict(d) for d in detalles_data]

            return resultado_completo

        except Exception as e:
            current_app.logger.error(f"Error al obtener resultado completo: {e}")
            return None