import base64
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Categoria, Edicion, EstadoBase, Festival, Opcion, TipoVotacion, Votacion


class OpcionesVisualesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        ahora = timezone.now()
        festival = Festival.objects.create(nombre="Festival visual", descripcion="Prueba")
        edicion = Edicion.objects.create(
            festival=festival, nombre="Edicion visual", anio=2031,
            fecha_inicio=ahora.date(), fecha_fin=(ahora + timedelta(days=5)).date(),
            estado=EstadoBase.ACTIVO,
        )
        categoria = Categoria.objects.create(
            edicion=edicion, nombre="Categoria visual", descripcion="Prueba",
            estado=EstadoBase.ACTIVO, visible_publicamente=True, orden=1,
        )
        tipo = TipoVotacion.objects.create(nombre="Tipo visual", activo=True)
        cls.votacion = Votacion.objects.create(
            categoria=categoria, tipo=tipo, nombre="Votacion visual",
            slug="votacion-visual-prueba", descripcion="Prueba visual",
            fecha_apertura=ahora - timedelta(hours=1),
            fecha_cierre=ahora + timedelta(hours=2),
            estado=Votacion.Estado.ABIERTA, publicada=True,
        )
        png = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwC"
            "AAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
        )
        cls.con_imagen = Opcion.objects.create(
            votacion=cls.votacion, nombre="Acordeon profesional",
            descripcion="Opcion con imagen",
            imagen=SimpleUploadedFile("acordeon.png", png, content_type="image/png"),
            orden=1, activa=True,
        )
        cls.sin_imagen = Opcion.objects.create(
            votacion=cls.votacion, nombre="Piqueria",
            descripcion="Opcion sin imagen", orden=2, activa=True,
        )
        cls.inactiva = Opcion.objects.create(
            votacion=cls.votacion, nombre="Opcion inactiva",
            descripcion="No debe aparecer", orden=3, activa=False,
        )
        cls.usuario = get_user_model().objects.create_user(
            username="usuario_visual", password="Temporal-Pruebas-2026"
        )

    def setUp(self):
        self.client.force_login(self.usuario)
        self.url = reverse("elecciones:participar", kwargs={"slug": self.votacion.slug})
        self.revisar_url = reverse("elecciones:revisar_voto", kwargs={"slug": self.votacion.slug})

    def test_muestra_opciones_activas_y_oculta_inactiva(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.con_imagen.nombre)
        self.assertContains(response, self.sin_imagen.nombre)
        self.assertNotContains(response, self.inactiva.nombre)

    def test_opcion_con_imagen_muestra_img(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.con_imagen.imagen.url)
        self.assertContains(response, 'class="vote-option__image js-option-image"')

    def test_opcion_sin_imagen_muestra_respaldo(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'class="vote-option__placeholder"')
        self.assertContains(response, ">P</span>", html=False)

    def test_conserva_un_radio_por_opcion_activa(self):
        response = self.client.get(self.url)
        self.assertEqual(response.content.count(b'type="radio"'), 2)
        self.assertContains(response, f'value="{self.con_imagen.pk}"')
        self.assertContains(response, f'value="{self.sin_imagen.pk}"')

    def test_seleccion_valida_redirige_a_revision(self):
        response = self.client.post(self.url, {"opcion": self.sin_imagen.pk})
        self.assertRedirects(response, self.revisar_url, fetch_redirect_response=False)
        clave = f"seleccion_votacion_{self.votacion.pk}"
        self.assertEqual(self.client.session[clave], self.sin_imagen.pk)

    def test_opcion_inactiva_es_rechazada(self):
        response = self.client.post(self.url, {"opcion": self.inactiva.pk})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors.get("opcion"))
        clave = f"seleccion_votacion_{self.votacion.pk}"
        self.assertNotIn(clave, self.client.session)
