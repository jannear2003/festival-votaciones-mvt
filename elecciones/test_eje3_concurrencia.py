from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier

from django.contrib.auth import get_user_model
from django.db import (
    IntegrityError,
    OperationalError,
    close_old_connections,
    transaction,
)
from django.test import TransactionTestCase
from django.utils import timezone

from elecciones.models import (
    Categoria,
    Edicion,
    EstadoBase,
    Festival,
    Opcion,
    Participacion,
    TipoVotacion,
    Votacion,
    Voto,
)


class ConcurrenciaEje3Tests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        ahora = timezone.now()

        self.festival = Festival.objects.create(
            nombre="Festival concurrencia Eje 3",
            descripcion="Prueba de solicitudes simultaneas",
        )

        self.edicion = Edicion.objects.create(
            festival=self.festival,
            nombre="Edicion concurrencia",
            anio=2032,
            fecha_inicio=ahora.date(),
            fecha_fin=(ahora + timedelta(days=10)).date(),
            estado=Edicion.Estado.ACTIVA,
        )

        self.categoria = Categoria.objects.create(
            edicion=self.edicion,
            nombre="Categoria concurrencia",
            descripcion="Categoria con dos subeventos",
            estado=EstadoBase.ACTIVO,
            visible_publicamente=True,
            orden=1,
        )

        self.tipo = TipoVotacion.objects.create(
            nombre="Tipo concurrencia Eje 3",
            activo=True,
        )

        self.votacion_uno = Votacion.objects.create(
            categoria=self.categoria,
            tipo=self.tipo,
            nombre="Subevento concurrente uno",
            slug="subevento-concurrente-uno",
            descripcion="Primer intento concurrente",
            fecha_apertura=ahora - timedelta(hours=1),
            fecha_cierre=ahora + timedelta(hours=4),
            estado=Votacion.Estado.ABIERTA,
            publicada=True,
        )

        self.votacion_dos = Votacion.objects.create(
            categoria=self.categoria,
            tipo=self.tipo,
            nombre="Subevento concurrente dos",
            slug="subevento-concurrente-dos",
            descripcion="Segundo intento concurrente",
            fecha_apertura=ahora - timedelta(hours=1),
            fecha_cierre=ahora + timedelta(hours=4),
            estado=Votacion.Estado.ABIERTA,
            publicada=True,
        )

        self.opcion_uno = Opcion.objects.create(
            votacion=self.votacion_uno,
            nombre="Opcion concurrente uno",
            activa=True,
            orden=1,
        )

        self.opcion_dos = Opcion.objects.create(
            votacion=self.votacion_dos,
            nombre="Opcion concurrente dos",
            activa=True,
            orden=1,
        )

        self.usuario = get_user_model().objects.create_user(
            username="usuario_concurrencia_eje3",
            email="concurrencia.eje3@example.com",
            password="Temporal-Concurrencia-2026",
        )

    @staticmethod
    def _registrar_intento(
        barrera,
        usuario_id,
        edicion_id,
        categoria_id,
        votacion_id,
        opcion_id,
        consecutivo,
    ):
        close_old_connections()

        try:
            Usuario = get_user_model()

            usuario = Usuario.objects.get(pk=usuario_id)
            edicion = Edicion.objects.get(pk=edicion_id)
            categoria = Categoria.objects.get(pk=categoria_id)
            votacion = Votacion.objects.get(pk=votacion_id)
            opcion = Opcion.objects.get(pk=opcion_id)

            barrera.wait(timeout=10)

            with transaction.atomic():
                participacion = Participacion.objects.create(
                    votacion=votacion,
                    categoria=categoria,
                    edicion=edicion,
                    usuario=usuario,
                    referencia=(
                        f"EJE3-CONCURRENTE-{consecutivo}"
                    ),
                    clave_sesion=(
                        f"sesion-concurrente-{consecutivo}"
                    ),
                    estado=Participacion.Estado.CONFIRMADA,
                    confirmada_en=timezone.now(),
                )

                voto = Voto(
                    participacion=participacion,
                    votacion=votacion,
                    opcion=opcion,
                )
                voto.full_clean()
                voto.save()

            return "registrado"

        except IntegrityError:
            return "rechazado_integridad"

        except OperationalError:
            return "rechazado_operacional"

        finally:
            close_old_connections()

    def test_cp09_dos_intentos_simultaneos_registran_un_voto(self):
        barrera = Barrier(2)

        argumentos = (
            (
                barrera,
                self.usuario.pk,
                self.edicion.pk,
                self.categoria.pk,
                self.votacion_uno.pk,
                self.opcion_uno.pk,
                1,
            ),
            (
                barrera,
                self.usuario.pk,
                self.edicion.pk,
                self.categoria.pk,
                self.votacion_dos.pk,
                self.opcion_dos.pk,
                2,
            ),
        )

        with ThreadPoolExecutor(max_workers=2) as executor:
            futuros = [
                executor.submit(
                    self._registrar_intento,
                    *argumento,
                )
                for argumento in argumentos
            ]

            resultados = [
                futuro.result(timeout=20)
                for futuro in futuros
            ]

        participaciones = Participacion.objects.filter(
            usuario=self.usuario,
            edicion=self.edicion,
            categoria=self.categoria,
            estado=Participacion.Estado.CONFIRMADA,
        )

        votos = Voto.objects.filter(
            participacion__usuario=self.usuario,
            participacion__edicion=self.edicion,
            participacion__categoria=self.categoria,
        )

        self.assertEqual(
            resultados.count("registrado"),
            1,
            resultados,
        )

        self.assertEqual(
            participaciones.count(),
            1,
            resultados,
        )

        self.assertEqual(
            votos.count(),
            1,
            resultados,
        )

        self.assertEqual(
            sum(
                resultado.startswith("rechazado")
                for resultado in resultados
            ),
            1,
            resultados,
        )
