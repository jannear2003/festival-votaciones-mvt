from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from elecciones.models import (
    Categoria,
    Edicion,
    EstadoBase,
    Festival,
    Participacion,
    TipoVotacion,
    Votacion,
)


class MisParticipacionesTests(TestCase):
    password = "Temporal-Pruebas-2026"

    @classmethod
    def setUpTestData(cls):
        ahora = timezone.now()

        cls.festival = Festival.objects.create(
            nombre="Festival historial",
            descripcion="Festival de prueba",
        )

        cls.edicion = Edicion.objects.create(
            festival=cls.festival,
            nombre="Edición historial",
            anio=2029,
            fecha_inicio=(
                ahora - timedelta(days=1)
            ).date(),
            fecha_fin=(
                ahora + timedelta(days=5)
            ).date(),
            estado=Edicion.Estado.ACTIVA,
        )

        cls.categoria = Categoria.objects.create(
            edicion=cls.edicion,
            nombre="Categoría historial",
            descripcion="Categoría de prueba",
            reglas="Reglas",
            orden=1,
            estado=EstadoBase.ACTIVO,
            visible_publicamente=True,
        )

        cls.tipo = TipoVotacion.objects.create(
            nombre="Tipo historial",
            descripcion="Tipo para pruebas",
            activo=True,
        )

        cls.votacion = Votacion.objects.create(
            categoria=cls.categoria,
            tipo=cls.tipo,
            nombre="Votación historial",
            slug="votacion-historial-prueba",
            descripcion="Votación para probar el historial",
            fecha_apertura=ahora - timedelta(hours=1),
            fecha_cierre=ahora + timedelta(hours=2),
            estado=Votacion.Estado.ABIERTA,
            publicada=True,
            resultados_publicos=False,
        )

        User = get_user_model()

        cls.usuario = User.objects.create_user(
            username="usuario_historial",
            email="historial@example.com",
            password=cls.password,
        )

        cls.otro_usuario = User.objects.create_user(
            username="otro_historial",
            email="otro-historial@example.com",
            password=cls.password,
        )

        cls.participacion = Participacion.objects.create(
            votacion=cls.votacion,
            usuario=cls.usuario,
            referencia="VOT-HISTORIAL-001",
            clave_sesion="sesion-historial-001",
            estado=Participacion.Estado.CONFIRMADA,
            confirmada_en=ahora,
        )

        cls.participacion_ajena = Participacion.objects.create(
            votacion=cls.votacion,
            usuario=cls.otro_usuario,
            referencia="VOT-HISTORIAL-AJENA",
            clave_sesion="sesion-historial-ajena",
            estado=Participacion.Estado.CONFIRMADA,
            confirmada_en=ahora - timedelta(minutes=10),
        )

        cls.participacion_historica = (
            Participacion.objects.create(
                votacion=cls.votacion,
                usuario=None,
                referencia="VOT-HISTORIAL-SIN-USUARIO",
                clave_sesion="sesion-historica",
                estado=Participacion.Estado.CONFIRMADA,
                confirmada_en=ahora - timedelta(days=1),
            )
        )

    def setUp(self):
        self.listado_url = reverse(
            "elecciones:mis_participaciones"
        )

        self.comprobante_url = reverse(
            "elecciones:comprobante_participacion",
            kwargs={
                "referencia": self.participacion.referencia,
            },
        )

    def test_visitante_es_redirigido_al_login(self):
        response = self.client.get(self.listado_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse("login"),
            response["Location"],
        )
        self.assertIn(
            "next=",
            response["Location"],
        )

    def test_usuario_sin_participaciones_ve_estado_vacio(self):
        usuario = get_user_model().objects.create_user(
            username="usuario_sin_participaciones",
            password=self.password,
        )

        self.client.force_login(usuario)

        response = self.client.get(self.listado_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Aún no tienes participaciones confirmadas",
        )
        self.assertContains(
            response,
            "Explorar votaciones",
        )

    def test_usuario_ve_su_participacion_confirmada(self):
        self.client.force_login(self.usuario)

        response = self.client.get(self.listado_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            self.votacion.nombre,
        )
        self.assertContains(
            response,
            self.participacion.referencia,
        )
        self.assertContains(
            response,
            self.categoria.nombre,
        )
        self.assertContains(
            response,
            self.edicion.nombre,
        )

    def test_usuario_no_ve_participacion_ajena(self):
        self.client.force_login(self.usuario)

        response = self.client.get(self.listado_url)

        self.assertNotContains(
            response,
            self.participacion_ajena.referencia,
        )

    def test_registro_historico_sin_usuario_no_aparece(self):
        self.client.force_login(self.usuario)

        response = self.client.get(self.listado_url)

        self.assertNotContains(
            response,
            self.participacion_historica.referencia,
        )

    def test_participacion_no_confirmada_no_aparece(self):
        Participacion.objects.create(
            votacion=self.votacion,
            usuario=get_user_model().objects.create_user(
                username="usuario_iniciado",
                password=self.password,
            ),
            referencia="VOT-HISTORIAL-INICIADA",
            clave_sesion="sesion-iniciada",
            estado=Participacion.Estado.INICIADA,
        )

        self.client.force_login(self.usuario)

        response = self.client.get(self.listado_url)

        self.assertNotContains(
            response,
            "VOT-HISTORIAL-INICIADA",
        )

    def test_comprobante_se_recupera_sin_dato_en_sesion(self):
        self.client.force_login(self.usuario)

        session = self.client.session
        session.flush()

        self.client.force_login(self.usuario)

        response = self.client.get(
            self.comprobante_url,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            self.participacion.referencia,
        )
        self.assertContains(
            response,
            self.votacion.nombre,
        )

    def test_usuario_no_puede_ver_comprobante_ajeno(self):
        self.client.force_login(self.usuario)

        url_ajena = reverse(
            "elecciones:comprobante_participacion",
            kwargs={
                "referencia": (
                    self.participacion_ajena.referencia
                ),
            },
        )

        response = self.client.get(url_ajena)

        self.assertEqual(response.status_code, 404)

    def test_referencia_inexistente_devuelve_404(self):
        self.client.force_login(self.usuario)

        response = self.client.get(
            reverse(
                "elecciones:comprobante_participacion",
                kwargs={
                    "referencia": "VOT-NO-EXISTE",
                },
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_comprobante_no_revela_opcion_seleccionada(self):
        self.client.force_login(self.usuario)

        response = self.client.get(
            self.comprobante_url,
        )

        self.assertContains(
            response,
            "no revela",
        )
        self.assertNotContains(
            response,
            "Opción seleccionada",
        )

    def test_navegacion_autenticada_muestra_enlace(self):
        self.client.force_login(self.usuario)

        response = self.client.get(
            reverse("elecciones:inicio")
        )

        self.assertContains(
            response,
            "Mis participaciones",
        )
        self.assertContains(
            response,
            f'href="{self.listado_url}"',
            html=False,
        )

    def test_navegacion_anonima_no_muestra_enlace(self):
        response = self.client.get(
            reverse("elecciones:inicio")
        )

        self.assertNotContains(
            response,
            "Mis participaciones",
        )

    def test_historial_no_muestra_identidad_de_otros_usuarios(self):
        self.client.force_login(self.usuario)

        response = self.client.get(self.listado_url)

        self.assertNotContains(
            response,
            self.otro_usuario.username,
        )
        self.assertNotContains(
            response,
            self.otro_usuario.email,
        )
