import os
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
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


class PrepararDemoEje3Tests(TestCase):
    password_publica = "Demo-Publica-Pruebas-2026"
    password_admin = "Demo-Admin-Pruebas-2026"

    @classmethod
    def setUpTestData(cls):
        cls.festival = Festival.objects.create(
            nombre="Festival de la Leyenda Vallenata",
            descripcion="Festival para pruebas del comando",
        )
        cls.edicion = Edicion.objects.create(
            festival=cls.festival,
            nombre="Festival de la Leyenda Vallenata 2027",
            anio=2027,
            fecha_inicio=timezone.now().date(),
            fecha_fin=(timezone.now() + timedelta(days=10)).date(),
            estado=Edicion.Estado.ACTIVA,
        )
        TipoVotacion.objects.create(
            nombre="Participación del público",
            descripcion="Tipo de votación para pruebas",
            activo=True,
        )
        Group.objects.create(name="Administrador general")

    def ejecutar_comando(self, *argumentos):
        variables = {
            "DEMO_EJE3_PASSWORD_PUBLICA": self.password_publica,
            "DEMO_EJE3_PASSWORD_ADMIN": self.password_admin,
        }
        with patch.dict(os.environ, variables, clear=False):
            call_command(
                "preparar_demo_eje3",
                *argumentos,
                verbosity=0,
            )

    def test_crea_estructura_controlada(self):
        self.ejecutar_comando()
        self.assertEqual(
            Categoria.objects.filter(
                nombre__startswith="Demo Eje 3"
            ).count(),
            3,
        )
        self.assertEqual(
            Votacion.objects.filter(
                slug__startswith="demo-eje3-"
            ).count(),
            4,
        )
        self.assertEqual(
            Opcion.objects.filter(
                votacion__slug__startswith="demo-eje3-"
            ).count(),
            12,
        )
        categoria_principal = Categoria.objects.get(
            nombre="Demo Eje 3 - Categoría principal"
        )
        self.assertEqual(categoria_principal.votaciones.count(), 2)

    def test_configura_usuarios_y_rol_administrativo(self):
        self.ejecutar_comando()
        User = get_user_model()
        usuario_a = User.objects.get(username="demo_eje3_a")
        usuario_b = User.objects.get(username="demo_eje3_b")
        admin = User.objects.get(username="demo_eje3_admin")
        self.assertTrue(usuario_a.check_password(self.password_publica))
        self.assertTrue(usuario_b.check_password(self.password_publica))
        self.assertTrue(admin.check_password(self.password_admin))
        self.assertFalse(usuario_a.is_staff)
        self.assertFalse(usuario_b.is_staff)
        self.assertTrue(admin.is_staff)
        self.assertFalse(admin.is_superuser)
        self.assertTrue(
            admin.groups.filter(name="Administrador general").exists()
        )

    def test_votaciones_habilitadas_tienen_fechas_vigentes(self):
        self.ejecutar_comando()
        ahora = timezone.now()
        habilitadas = Votacion.objects.filter(
            slug__in=[
                "demo-eje3-subevento-uno",
                "demo-eje3-subevento-dos",
                "demo-eje3-votacion-alternativa",
            ]
        )
        self.assertEqual(habilitadas.count(), 3)
        for votacion in habilitadas:
            with self.subTest(slug=votacion.slug):
                self.assertEqual(votacion.estado, Votacion.Estado.ABIERTA)
                self.assertTrue(votacion.publicada)
                self.assertLessEqual(votacion.fecha_apertura, ahora)
                self.assertGreater(votacion.fecha_cierre, ahora)

    def test_categoria_negativa_no_esta_habilitada(self):
        self.ejecutar_comando()
        categoria = Categoria.objects.get(
            nombre="Demo Eje 3 - Categoría no habilitada"
        )
        votacion = Votacion.objects.get(slug="demo-eje3-no-habilitada")
        self.assertEqual(categoria.estado, EstadoBase.BORRADOR)
        self.assertFalse(categoria.visible_publicamente)
        self.assertEqual(votacion.estado, Votacion.Estado.BORRADOR)
        self.assertFalse(votacion.publicada)

    def test_segunda_ejecucion_no_duplica_registros(self):
        self.ejecutar_comando()
        self.ejecutar_comando()
        self.assertEqual(
            Categoria.objects.filter(
                nombre__startswith="Demo Eje 3"
            ).count(),
            3,
        )
        self.assertEqual(
            Votacion.objects.filter(
                slug__startswith="demo-eje3-"
            ).count(),
            4,
        )
        self.assertEqual(
            Opcion.objects.filter(
                votacion__slug__startswith="demo-eje3-"
            ).count(),
            12,
        )
        self.assertEqual(
            get_user_model().objects.filter(
                username__startswith="demo_eje3_"
            ).count(),
            3,
        )

    def test_reinicio_elimina_solo_votos_demo(self):
        self.ejecutar_comando()
        User = get_user_model()
        usuario_demo = User.objects.get(username="demo_eje3_a")
        categoria_demo = Categoria.objects.get(
            nombre="Demo Eje 3 - Categoría principal"
        )
        votacion_demo = Votacion.objects.get(
            slug="demo-eje3-subevento-uno"
        )
        opcion_demo = votacion_demo.opciones.first()
        participacion_demo = Participacion.objects.create(
            votacion=votacion_demo,
            categoria=categoria_demo,
            edicion=self.edicion,
            usuario=usuario_demo,
            referencia="VOT-DEMO-REINICIO",
            clave_sesion="sesion-demo-reinicio",
            estado=Participacion.Estado.CONFIRMADA,
            confirmada_en=timezone.now(),
        )
        Voto.objects.create(
            participacion=participacion_demo,
            votacion=votacion_demo,
            opcion=opcion_demo,
        )
        usuario_externo = User.objects.create_user(
            username="usuario_no_demo",
            password="Temporal-No-Demo-2026",
        )
        categoria_externa = Categoria.objects.create(
            edicion=self.edicion,
            nombre="Categoría externa",
            estado=EstadoBase.ACTIVO,
            visible_publicamente=True,
        )
        tipo = TipoVotacion.objects.get(
            nombre="Participación del público"
        )
        votacion_externa = Votacion.objects.create(
            categoria=categoria_externa,
            tipo=tipo,
            nombre="Votación externa",
            slug="votacion-externa-reinicio",
            descripcion="No debe eliminarse",
            fecha_apertura=timezone.now() - timedelta(hours=1),
            fecha_cierre=timezone.now() + timedelta(hours=3),
            estado=Votacion.Estado.ABIERTA,
            publicada=True,
        )
        opcion_externa = Opcion.objects.create(
            votacion=votacion_externa,
            nombre="Opción externa",
            activa=True,
        )
        participacion_externa = Participacion.objects.create(
            votacion=votacion_externa,
            categoria=categoria_externa,
            edicion=self.edicion,
            usuario=usuario_externo,
            referencia="VOT-EXTERNO-CONSERVAR",
            clave_sesion="sesion-externa",
            estado=Participacion.Estado.CONFIRMADA,
            confirmada_en=timezone.now(),
        )
        Voto.objects.create(
            participacion=participacion_externa,
            votacion=votacion_externa,
            opcion=opcion_externa,
        )
        self.ejecutar_comando("--reiniciar-votos")
        self.assertFalse(
            Participacion.objects.filter(pk=participacion_demo.pk).exists()
        )
        self.assertTrue(
            Participacion.objects.filter(pk=participacion_externa.pk).exists()
        )
