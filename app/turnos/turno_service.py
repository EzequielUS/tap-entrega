# app/services/turno_service.py
from flask import current_app
from ..dao.turno_dao import TurnoDAO
from ..dao.vehiculo_dao import VehiculoDAO
from ..dao.resultado_dao import ResultadoDAO
from ..models import Vehiculo, Resultado, ResultadoPorControl
from datetime import datetime

class TurnoService:
    def __init__(self, turno_dao: TurnoDAO, vehiculo_dao: VehiculoDAO, resultado_dao: ResultadoDAO):
        self.turno_dao = turno_dao
        self.vehiculo_dao = vehiculo_dao
        self.resultado_dao = resultado_dao

    def consultar_disponibilidad(self, fecha_str: str):
        """ Consulta los slots LIBRES para una fecha específica. Se asume que los slots han sido precargados en la DB usando el init.sql. """
        try:
            fecha_consulta = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            current_app.logger.error(f"Formato de fecha inválido recibido: {fecha_str}")
            return None, "Formato de fecha inválido. Usar YYYY-MM-DD."

        disponibles = self.turno_dao.obtener_disponibles_por_fecha(fecha_consulta)
        current_app.logger.info(f"Turnos disponibles para {fecha_str}: {len(disponibles)} encontrados.")
        return [turno.to_dict() for turno in disponibles], None

    def reservar_turno(self, matricula: str, id_marca: int, anio: int, id_turno: int):
        """ Generar una reserva de turno para un vehículo. """

        vehiculo = Vehiculo(matricula=matricula, id_marca=id_marca, anio=anio)
        self.vehiculo_dao.crear(vehiculo)

        turno = self.turno_dao.obtener_por_id(id_turno)
        if not turno:
            return None, "ID de turno no encontrado."

        if turno.estado != 'LIBRE':
            return None, f"El turno {id_turno} ya está {turno.estado}."

        turno_actualizado = self.turno_dao.actualizar_a_reservado(id_turno, matricula)
        if turno_actualizado:
            return turno_actualizado.to_dict(), None
        else:
            return None, "Error al actualizar el estado del turno."

    def consultar_turno(self, id_turno: int):
        """ Obtiene el turno y, si está finalizado, obtiene el resultado completo. """
        turno = self.turno_dao.obtener_por_id(id_turno)
        if not turno:
            return None, "Turno no encontrado."

        turno_dict = turno.to_dict()
        if turno.estado == 'FINALIZADO' and turno.id_resultado:
            resultado_completo = self.resultado_dao.obtener_resultado_completo(turno.id_resultado)
            current_app.logger.info(f"Resultado completo obtenido para turno ID: {id_turno}")
            turno_dict['resultado_inspeccion'] = resultado_completo
        else:
            current_app.logger.info(f"Turno {id_turno} no tiene resultado de inspección.")
            turno_dict['resultado_inspeccion'] = None

        return turno_dict, None

    def consultar_turnos_pendientes(self):
        """ Obtiene todos los turnos en estado 'RESERVADO'. """
        pendientes = self.turno_dao.obtener_pendientes()
        return [turno.to_dict() for turno in pendientes], None

    def _procesar_detalles_inspeccion(self, detalles_control: list):
        """ Procesa la lista de detalles, calcula puntajes y valida. """
        puntaje_total = 0
        falla_critica_encontrada = False
        detalles_control_objetos = []

        for d in detalles_control:
            calificacion = d.get('calificacion')
            if calificacion is None or not (1 <= calificacion <= 10):
                return None, False, [], "Calificación inválida. Debe ser entre 1 y 10."

            puntaje_total += calificacion
            if calificacion < 5:
                falla_critica_encontrada = True

            detalles_control_objetos.append(ResultadoPorControl(
                id_control=d.get('id_control'),
                calificacion=calificacion,
                observaciones=d.get('observaciones')
            ))

        return puntaje_total, falla_critica_encontrada, detalles_control_objetos, None

    def _determinar_resultado_final(self, puntaje_total: int, falla_critica: bool) -> str:
        """Determina el estado final de la inspección basado en las reglas de negocio."""
        if puntaje_total < 40 or falla_critica:
            return 'RECHEQUEAR'
        elif puntaje_total >= 80:
            return 'SEGURO'
        else:
            return 'SEGURO CON ADVERTENCIA'

    def finalizar_turno_inspeccion(self, id_turno: int, detalles_control: list):
        """ Finaliza un turno de inspección, calcula y guarda el resultado. """
        turno = self.turno_dao.obtener_por_id(id_turno)
        if not turno or turno.estado != 'RESERVADO':
            return None, "Turno no encontrado o no está listo para ser finalizado."

        puntaje, falla, detalles_obj, error = self._procesar_detalles_inspeccion(detalles_control)
        if error:
            return None, error

        resultado_final = self._determinar_resultado_final(puntaje, falla)

        resultado_cabecera = Resultado(
            resultado=resultado_final,
            puntaje_total=puntaje,
            observaciones=f"Resultado automatico: {resultado_final} con {puntaje}/80 puntos."
        )

        id_resultado = self.resultado_dao.registrar_resultado_inspeccion(
            turno,
            resultado_cabecera,
            detalles_obj
        )

        if id_resultado:
            current_app.logger.info(f"Turno ID {id_turno} finalizado y guardado exitosamente en DB con resultado ID: {id_resultado}.")
            return {'id_turno': id_turno, 'resultado': resultado_final}, None
        else:
            current_app.logger.error(f"Fallo crítico al guardar la transacción en la DB para el turno ID: {id_turno}")
            return None, "Error al guardar la transacción de resultados en la DB."