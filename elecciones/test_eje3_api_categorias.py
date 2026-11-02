from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from elecciones.models import (
    Categoria,
    Edicion,
    EstadoBase,
    Festival,
    Opcion,
    TipoVotacion,
    Votacion,
)


class ApiCategoriasEje3Tests(TestCase):

    @classmethod
    def setUpTestData(cls):
        ahora = timezone.now()

        cls.festival = Festival.objects.create(
            nombre="Festival API Eje 3",
            descripcion="Datos controlados para la API",
        )

        cls.edicion = Edicion.objects.create(
            festival=cls.festival,
            nombre="Edicion activa API",
            anio=2031,
            fecha_inicio=ahora.date(),
            fecha_fin=(ahora + timedelta(days=10)).date(),
            estado=Edicion.Estado.ACTIVA,
        )

        cls.categoria_visible = Categoria.objects.create(
            edicion=cls.edicion,
            nombre="Categoria visible API",
            descripcion="Debe aparecer",
            estado=EstadoBase.ACTIVO,
            visible_publicamente=True,
            orden=1,
        )

        cls.categoria_oculta = Categoria.objects.create(
            edicion=cls.edicion,
            nombre="Categoria oculta API",
            descripcion="No debe aparecer",
            estado=EstadoBase.ACTIVO,
            visible_publicamente=False,
            orden=2,
        )

        cls.tipo = TipoVotacion.objects.create(
            nombre="Tipo API Eje 3",
            activo=True,
        )

        cls.votacion_publicada = Votacion.objects.create(
            categoria=cls.categoria_visible,
            tipo=cls.tipo,
            nombre="Votacion publicada API",
            slug="votacion-publicada-api-eje3",
            descripcion="Debe aparecer",
            fecha_apertura=ahora - timedelta(hours=1),
            fecha_cierre=ahora + timedelta(hours=3),
            estado=Votacion.Estado.ABIERTA,
            publicada=True,
        )

        cls.votacion_no_publicada = Votacion.objects.create(
            categoria=cls.categoria_visible,
            tipo=cls.tipo,
            nombre="Votacion privada API",
            slug="votacion-privada-api-eje3",
            descripcion="No debe aparecer",
            fecha_apertura=ahora - timedelta(hours=1),
            fecha_cierre=ahora + timedelta(hours=3),
            estado=Votacion.Estado.ABIERTA,
            publicada=False,
        )

        cls.opcion_activa = Opcion.objects.create(
            votacion=cls.votacion_publicada,
            nombre="Opcion activa API",
            descripcion="Debe aparecer",
            activa=True,
            orden=1,
        )

        cls.opcion_inactiva = Opcion.objects.create(
            votacion=cls.votacion_publicada,
            nombre="Opcion inactiva API",
            descripcion="No debe aparecer",
            activa=False,
            orden=2,
        )

        cls.url = reverse("elecciones:api_categorias")

    def test_cp10_get_devuelve_json_valido(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/json",
        )

        datos = response.json()

        self.assertIn("edicion", datos)
        self.assertIn("categorias", datos)

    def test_cp10_devuelve_edicion_activa(self):
        datos = self.client.get(self.url).json()

        self.assertEqual(
            datos["edicion"]["id"],
            self.edicion.pk,
        )
        self.assertEqual(
            datos["edicion"]["nombre"],
            self.edicion.nombre,
        )
        self.assertEqual(
            datos["edicion"]["anio"],
            self.edicion.anio,
        )

    def test_cp10_incluye_categoria_y_opciones_reales(self):
        datos = self.client.get(self.url).json()

        self.assertEqual(len(datos["categorias"]), 1)

        categoria = datos["categorias"][0]

        self.assertEqual(
            categoria["id"],
            self.categoria_visible.pk,
        )
        self.assertEqual(
            categoria["nombre"],
            self.categoria_visible.nombre,
        )
        self.assertEqual(len(categoria["votaciones"]), 1)

        votacion = categoria["votaciones"][0]

        self.assertEqual(
            votacion["id"],
            self.votacion_publicada.pk,
        )
        self.assertEqual(len(votacion["opciones"]), 1)
        self.assertEqual(
            votacion["opciones"][0]["id"],
            self.opcion_activa.pk,
        )

    def test_cp10_excluye_datos_no_publicables(self):
        contenido = self.client.get(
            self.url
        ).content.decode("utf-8")

        self.assertNotIn(
            self.categoria_oculta.nombre,
            contenido,
        )
        self.assertNotIn(
            self.votacion_no_publicada.nombre,
            contenido,
        )
        self.assertNotIn(
            self.opcion_inactiva.nombre,
            contenido,
        )

    def test_cp10_no_expone_datos_sensibles(self):
        texto = str(
            self.client.get(self.url).json()
        ).lower()

        for campo_sensible in (
            "usuario",
            "email",
            "clave_sesion",
            "referencia",
            "password",
            "participacion",
            "registrado_en",
        ):
            self.assertNotIn(campo_sensible, texto)

    def test_cp10_sin_edicion_activa_devuelve_lista_vacia(self):
        self.edicion.estado = Edicion.Estado.CERRADA
        self.edicion.save(update_fields=["estado"])

        response = self.client.get(self.url)
        datos = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(datos["edicion"])
        self.assertEqual(datos["categorias"], [])

    def test_cp10_rechaza_metodos_distintos_de_get(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response["Allow"], "GET")
