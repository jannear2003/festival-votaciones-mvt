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
    PublicacionResultado,
    TipoVotacion,
    Votacion,
)


class AccesoResultadosPublicosTests(TestCase):
    password = "Temporal-Pruebas-2026"

    @classmethod
    def setUpTestData(cls):
        ahora = timezone.now()

        cls.festival = Festival.objects.create(
            nombre="Festival resultados públicos",
            descripcion="Festival para probar resultados públicos",
        )

        cls.edicion = Edicion.objects.create(
            festival=cls.festival,
            nombre="Edición resultados públicos",
            anio=2030,
            fecha_inicio=(ahora - timedelta(days=5)).date(),
            fecha_fin=(ahora + timedelta(days=5)).date(),
            estado=Edicion.Estado.ACTIVA,
        )

        cls.categoria = Categoria.objects.create(
            edicion=cls.edicion,
            nombre="Categoría resultados públicos",
            descripcion="Categoría para pruebas",
            reglas="Reglas de prueba",
            orden=1,
            estado=EstadoBase.ACTIVO,
            visible_publicamente=True,
        )

        cls.tipo = TipoVotacion.objects.create(
            nombre="Tipo resultados públicos",
            descripcion="Tipo de votación para pruebas",
            activo=True,
        )

        cls.votacion = Votacion.objects.create(
            categoria=cls.categoria,
            tipo=cls.tipo,
            nombre="Votación con resultados públicos",
            slug="votacion-resultados-publicos",
            descripcion="Votación para validar el acceso público",
            fecha_apertura=ahora - timedelta(days=2),
            fecha_cierre=ahora - timedelta(days=1),
            estado=Votacion.Estado.CERRADA,
            publicada=True,
            resultados_publicos=True,
        )

        User = get_user_model()

        cls.administrador = User.objects.create_user(
            username="administrador_resultados",
            email="administrador-resultados@example.com",
            password=cls.password,
            is_staff=True,
        )

        cls.resumen = {
            "total_votos": 3,
            "opciones": [
                {
                    "opcion_id": 1,
                    "nombre": "Opción A",
                    "total": 2,
                    "porcentaje": 66.67,
                },
                {
                    "opcion_id": 2,
                    "nombre": "Opción B",
                    "total": 1,
                    "porcentaje": 33.33,
                },
            ],
        }

        cls.publicacion = PublicacionResultado.objects.create(
            votacion=cls.votacion,
            version=1,
            resumen=cls.resumen,
            observacion="Publicación inicial para pruebas",
            publicada_por=cls.administrador,
            activa=True,
        )

    def setUp(self):
        self.url = reverse(
            "elecciones:resultado_publico",
            kwargs={"slug": self.votacion.slug},
        )

    def test_visitante_puede_consultar_resultado_publicado(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "elecciones/resultado_publico.html",
        )
        self.assertEqual(
            response.context["votacion"],
            self.votacion,
        )
        self.assertEqual(
            response.context["publicacion"],
            self.publicacion,
        )
        self.assertEqual(
            response.context["resumen"],
            self.resumen,
        )

    def test_resultado_publico_no_exige_autenticacion(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_votacion_sin_resultados_publicos_devuelve_404(self):
        self.votacion.resultados_publicos = False
        self.votacion.save(update_fields=["resultados_publicos"])

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    def test_votacion_sin_publicacion_activa_devuelve_404(self):
        self.publicacion.activa = False
        self.publicacion.retirada_en = timezone.now()
        self.publicacion.save(
            update_fields=["activa", "retirada_en"],
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    def test_slug_inexistente_devuelve_404(self):
        url = reverse(
            "elecciones:resultado_publico",
            kwargs={"slug": "resultado-publico-inexistente"},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
