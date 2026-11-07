import os
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
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


class Command(BaseCommand):
    help = (
        "Prepara datos controlados para demostrar "
        "los casos CP-01 a CP-10 del Eje 3."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--reiniciar-votos",
            action="store_true",
            help=(
                "Elimina únicamente votos y participaciones "
                "de las cuentas demo_eje3_*."
            ),
        )

    @transaction.atomic
    def handle(self, *args, **options):
        password_publica = os.getenv(
            "DEMO_EJE3_PASSWORD_PUBLICA"
        )
        password_admin = os.getenv(
            "DEMO_EJE3_PASSWORD_ADMIN"
        )

        if not password_publica or not password_admin:
            raise CommandError(
                "Defina DEMO_EJE3_PASSWORD_PUBLICA y "
                "DEMO_EJE3_PASSWORD_ADMIN en la terminal."
            )

        festival = Festival.objects.get(
            nombre="Festival de la Leyenda Vallenata"
        )

        edicion = Edicion.objects.get(
            festival=festival,
            anio=2027,
        )

        tipo = TipoVotacion.objects.get(
            nombre="Participación del público",
            activo=True,
        )

        User = get_user_model()

        usuario_a, _ = User.objects.get_or_create(
            username="demo_eje3_a",
            defaults={
                "first_name": "Usuario",
                "last_name": "Demostración A",
                "email": "demo.eje3.a@example.local",
                "is_active": True,
            },
        )
        usuario_a.set_password(password_publica)
        usuario_a.is_staff = False
        usuario_a.is_superuser = False
        usuario_a.save()

        usuario_b, _ = User.objects.get_or_create(
            username="demo_eje3_b",
            defaults={
                "first_name": "Usuario",
                "last_name": "Demostración B",
                "email": "demo.eje3.b@example.local",
                "is_active": True,
            },
        )
        usuario_b.set_password(password_publica)
        usuario_b.is_staff = False
        usuario_b.is_superuser = False
        usuario_b.save()

        usuario_admin, _ = User.objects.get_or_create(
            username="demo_eje3_admin",
            defaults={
                "first_name": "Administrador",
                "last_name": "Demostración Eje 3",
                "email": "demo.eje3.admin@example.local",
                "is_active": True,
            },
        )
        usuario_admin.set_password(password_admin)
        usuario_admin.is_staff = True
        usuario_admin.is_superuser = False
        usuario_admin.save()

        grupo_admin = Group.objects.get(
            name="Administrador general"
        )
        usuario_admin.groups.set([grupo_admin])

        usuarios_demo = [
            usuario_a,
            usuario_b,
            usuario_admin,
        ]

        if options["reiniciar_votos"]:
            participaciones = Participacion.objects.filter(
                usuario__in=usuarios_demo
            )
            votos = Voto.objects.filter(
                participacion__in=participaciones
            )

            total_votos = votos.count()
            total_participaciones = participaciones.count()

            votos.delete()
            participaciones.delete()

            self.stdout.write(
                self.style.WARNING(
                    "Reinicio controlado: "
                    f"{total_votos} votos y "
                    f"{total_participaciones} participaciones "
                    "de demostración eliminados."
                )
            )

        categoria_a, _ = Categoria.objects.update_or_create(
            edicion=edicion,
            nombre="Demo Eje 3 - Categoría principal",
            defaults={
                "descripcion": (
                    "Categoría con dos subeventos para "
                    "demostrar unicidad por categoría."
                ),
                "reglas": (
                    "Cada usuario puede emitir un único voto "
                    "en esta categoría para la edición."
                ),
                "orden": 90,
                "estado": EstadoBase.ACTIVO,
                "visible_publicamente": True,
            },
        )

        categoria_b, _ = Categoria.objects.update_or_create(
            edicion=edicion,
            nombre="Demo Eje 3 - Categoría alternativa",
            defaults={
                "descripcion": (
                    "Categoría diferente para demostrar "
                    "una participación adicional permitida."
                ),
                "reglas": "Datos controlados del Eje 3.",
                "orden": 91,
                "estado": EstadoBase.ACTIVO,
                "visible_publicamente": True,
            },
        )

        categoria_no_habilitada, _ = (
            Categoria.objects.update_or_create(
                edicion=edicion,
                nombre=(
                    "Demo Eje 3 - Categoría no habilitada"
                ),
                defaults={
                    "descripcion": (
                        "Categoría para demostrar rechazo "
                        "de operaciones no habilitadas."
                    ),
                    "reglas": "Datos controlados del Eje 3.",
                    "orden": 92,
                    "estado": EstadoBase.BORRADOR,
                    "visible_publicamente": False,
                },
            )
        )

        ahora = timezone.now()
        apertura = ahora - timedelta(hours=1)
        cierre = ahora + timedelta(days=7)

        votacion_a1 = self._preparar_votacion(
            categoria=categoria_a,
            tipo=tipo,
            slug="demo-eje3-subevento-uno",
            nombre="Demo Eje 3 - Subevento uno",
            descripcion=(
                "Primera votación de la categoría principal."
            ),
            apertura=apertura,
            cierre=cierre,
            publicada=True,
            estado=Votacion.Estado.ABIERTA,
        )

        votacion_a2 = self._preparar_votacion(
            categoria=categoria_a,
            tipo=tipo,
            slug="demo-eje3-subevento-dos",
            nombre="Demo Eje 3 - Subevento dos",
            descripcion=(
                "Segunda votación de la misma categoría."
            ),
            apertura=apertura,
            cierre=cierre,
            publicada=True,
            estado=Votacion.Estado.ABIERTA,
        )

        votacion_b1 = self._preparar_votacion(
            categoria=categoria_b,
            tipo=tipo,
            slug="demo-eje3-votacion-alternativa",
            nombre="Demo Eje 3 - Votación alternativa",
            descripcion=(
                "Votación de una categoría diferente."
            ),
            apertura=apertura,
            cierre=cierre,
            publicada=True,
            estado=Votacion.Estado.ABIERTA,
        )

        votacion_no_habilitada = self._preparar_votacion(
            categoria=categoria_no_habilitada,
            tipo=tipo,
            slug="demo-eje3-no-habilitada",
            nombre="Demo Eje 3 - Votación no habilitada",
            descripcion=(
                "Votación destinada a demostrar el rechazo."
            ),
            apertura=apertura,
            cierre=cierre,
            publicada=False,
            estado=Votacion.Estado.BORRADOR,
        )

        for votacion in (
            votacion_a1,
            votacion_a2,
            votacion_b1,
            votacion_no_habilitada,
        ):
            self._preparar_opciones(votacion)

        self.stdout.write(
            self.style.SUCCESS(
                "Datos de demostración del Eje 3 preparados."
            )
        )
        self.stdout.write(
            f"Edición: {edicion.nombre}"
        )
        self.stdout.write(
            f"Categoría principal: {categoria_a.nombre}"
        )
        self.stdout.write(
            f"Categoría alternativa: {categoria_b.nombre}"
        )
        self.stdout.write(
            "Categoría no habilitada: "
            f"{categoria_no_habilitada.nombre}"
        )
        self.stdout.write(
            "Usuarios: demo_eje3_a, demo_eje3_b, "
            "demo_eje3_admin"
        )
        self.stdout.write(
            f"Vigencia de votaciones: {apertura} a {cierre}"
        )

    def _preparar_votacion(
        self,
        *,
        categoria,
        tipo,
        slug,
        nombre,
        descripcion,
        apertura,
        cierre,
        publicada,
        estado,
    ):
        votacion, _ = Votacion.objects.update_or_create(
            slug=slug,
            defaults={
                "categoria": categoria,
                "tipo": tipo,
                "nombre": nombre,
                "descripcion": descripcion,
                "fecha_apertura": apertura,
                "fecha_cierre": cierre,
                "estado": estado,
                "publicada": publicada,
                "resultados_publicos": False,
            },
        )

        votacion.full_clean()
        votacion.save()
        return votacion

    def _preparar_opciones(self, votacion):
        nombres = (
            "Participante Demo 01",
            "Participante Demo 02",
            "Participante Demo 03",
        )

        for orden, nombre in enumerate(nombres, start=1):
            opcion, _ = Opcion.objects.update_or_create(
                votacion=votacion,
                nombre=nombre,
                defaults={
                    "descripcion": (
                        f"Opción ficticia de {votacion.nombre}."
                    ),
                    "orden": orden,
                    "activa": True,
                },
            )
            opcion.full_clean()
            opcion.save()