import base64
import shutil
import tempfile
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import timezone

from .forms import CategoriaForm, OpcionForm, VotacionForm
from .models import (
    Categoria,
    Edicion,
    EstadoBase,
    Festival,
    Opcion,
    TipoVotacion,
    Votacion,
)
from .validators import (
    TAMANO_MAXIMO_IMAGEN,
    validar_imagen_configurable,
)


PNG_VALIDO = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAB"
    "CAQAAAC1HAwCAAAAC0lEQVR42mNk"
    "YAAAAAYAAjCB0C8AAAAASUVORK5CYII="
)


def imagen_png(nombre="imagen.png"):
    return SimpleUploadedFile(
        nombre,
        PNG_VALIDO,
        content_type="image/png",
    )


MEDIA_ROOT_PRUEBAS = tempfile.mkdtemp(
    prefix="festival-media-tests-",
)


@override_settings(
    MEDIA_ROOT=MEDIA_ROOT_PRUEBAS,
)
class ImagenesConfigurablesTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(
            MEDIA_ROOT_PRUEBAS,
            ignore_errors=True,
        )

    @classmethod
    def setUpTestData(cls):
        ahora = timezone.now()

        cls.festival = Festival.objects.create(
            nombre="Festival para imágenes",
            descripcion="Datos de prueba",
        )

        cls.edicion = Edicion.objects.create(
            festival=cls.festival,
            nombre="Edición para imágenes",
            anio=2028,
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
            nombre="Categoría visual",
            descripcion="Categoría de prueba",
            reglas="Reglas de prueba",
            orden=1,
            estado=EstadoBase.ACTIVO,
            visible_publicamente=True,
        )

        cls.tipo = TipoVotacion.objects.create(
            nombre="Tipo visual",
            descripcion="Tipo de prueba",
            activo=True,
        )

        cls.votacion = Votacion.objects.create(
            categoria=cls.categoria,
            tipo=cls.tipo,
            nombre="Votación visual",
            slug="votacion-visual-imagenes",
            descripcion="Votación de prueba",
            fecha_apertura=ahora - timedelta(hours=1),
            fecha_cierre=ahora + timedelta(hours=2),
            estado=Votacion.Estado.ABIERTA,
            publicada=True,
            resultados_publicos=False,
        )

        cls.opcion = Opcion.objects.create(
            votacion=cls.votacion,
            nombre="Opción visual",
            descripcion="Alternativa de prueba",
            orden=1,
            activa=True,
        )

    def test_modelos_tienen_campos_de_imagen(self):
        self.assertEqual(
            Categoria._meta.get_field(
                "imagen"
            ).upload_to,
            "categorias/",
        )
        self.assertEqual(
            Votacion._meta.get_field(
                "imagen"
            ).upload_to,
            "votaciones/",
        )
        self.assertEqual(
            Opcion._meta.get_field(
                "imagen"
            ).upload_to,
            "opciones/",
        )

    def test_formularios_son_multipart(self):
        self.assertTrue(
            CategoriaForm().is_multipart()
        )
        self.assertTrue(
            VotacionForm().is_multipart()
        )
        self.assertTrue(
            OpcionForm().is_multipart()
        )

    def test_formularios_incluyen_imagen(self):
        self.assertIn(
            "imagen",
            CategoriaForm().fields,
        )
        self.assertIn(
            "imagen",
            VotacionForm().fields,
        )
        self.assertIn(
            "imagen",
            OpcionForm().fields,
        )

    def test_categoria_acepta_png_valido(self):
        form = CategoriaForm(
            data={
                "edicion": self.edicion.pk,
                "nombre": "Categoría con imagen",
                "descripcion": "Descripción",
                "reglas": "Reglas",
                "orden": 2,
                "estado": EstadoBase.BORRADOR,
                "visible_publicamente": False,
            },
            files={
                "imagen": imagen_png(
                    "categoria.png"
                ),
            },
        )

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

    def test_votacion_acepta_png_valido(self):
        ahora = timezone.now()

        form = VotacionForm(
            data={
                "categoria": self.categoria.pk,
                "tipo": self.tipo.pk,
                "nombre": "Votación con imagen",
                "slug": "votacion-con-imagen",
                "descripcion": "Descripción",
                "fecha_apertura": (
                    ahora - timedelta(hours=1)
                ).strftime("%Y-%m-%dT%H:%M"),
                "fecha_cierre": (
                    ahora + timedelta(hours=2)
                ).strftime("%Y-%m-%dT%H:%M"),
                "estado": Votacion.Estado.ABIERTA,
                "publicada": True,
                "resultados_publicos": False,
            },
            files={
                "imagen": imagen_png(
                    "votacion.png"
                ),
            },
        )

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

    def test_opcion_acepta_png_valido(self):
        form = OpcionForm(
            data={
                "nombre": "Opción con imagen",
                "descripcion": "Descripción",
                "orden": 3,
                "activa": True,
            },
            files={
                "imagen": imagen_png(
                    "opcion.png"
                ),
            },
        )

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

    def test_extension_no_permitida_es_rechazada(self):
        archivo = SimpleUploadedFile(
            "archivo.exe",
            PNG_VALIDO,
            content_type="image/png",
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Formato no permitido",
        ):
            validar_imagen_configurable(
                archivo
            )

    def test_tipo_mime_no_permitido_es_rechazado(self):
        archivo = SimpleUploadedFile(
            "archivo.png",
            PNG_VALIDO,
            content_type="application/octet-stream",
        )

        with self.assertRaisesMessage(
            ValidationError,
            "El tipo de archivo",
        ):
            validar_imagen_configurable(
                archivo
            )

    def test_archivo_mayor_a_cinco_mb_es_rechazado(self):
        archivo = SimpleUploadedFile(
            "grande.png",
            b"x" * (
                TAMANO_MAXIMO_IMAGEN + 1
            ),
            content_type="image/png",
        )

        with self.assertRaisesMessage(
            ValidationError,
            "no puede superar 5 MB",
        ):
            validar_imagen_configurable(
                archivo
            )

    def test_contenido_falso_con_extension_png_es_rechazado(self):
        archivo = SimpleUploadedFile(
            "imagen.png",
            b"esto no es una imagen real",
            content_type="image/png",
        )

        form = OpcionForm(
            data={
                "nombre": "Opción inválida",
                "descripcion": "",
                "orden": 4,
                "activa": True,
            },
            files={"imagen": archivo},
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "imagen",
            form.errors,
        )

    def test_edicion_sin_archivo_conserva_imagen_actual(self):
        self.opcion.imagen = imagen_png(
            "imagen-existente.png"
        )
        self.opcion.save(
            update_fields=["imagen"]
        )

        nombre_original = (
            self.opcion.imagen.name
        )

        form = OpcionForm(
            data={
                "nombre": self.opcion.nombre,
                "descripcion": (
                    self.opcion.descripcion
                ),
                "orden": self.opcion.orden,
                "activa": self.opcion.activa,
            },
            instance=self.opcion,
        )

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

        opcion = form.save()

        self.assertEqual(
            opcion.imagen.name,
            nombre_original,
        )

    def test_portal_usa_imagen_de_votacion(self):
        self.votacion.imagen = imagen_png(
            "portada-portal.png"
        )
        self.votacion.save(
            update_fields=["imagen"]
        )

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            self.votacion.nombre,
        )
        self.assertContains(
            response,
            self.votacion.imagen.url,
        )

    def test_portal_usa_imagen_de_categoria_como_respaldo(self):
        self.categoria.imagen = imagen_png(
            "categoria-respaldo.png"
        )
        self.categoria.save(
            update_fields=["imagen"]
        )

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            self.votacion.nombre,
        )
        self.assertContains(
            response,
            self.categoria.imagen.url,
        )

    def test_detalle_muestra_imagen_de_opcion(self):
        self.opcion.imagen = imagen_png(
            "opcion-detalle.png"
        )
        self.opcion.save(
            update_fields=["imagen"]
        )

        response = self.client.get(
            self.votacion.get_absolute_url()
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            self.opcion.imagen.url,
        )
        self.assertContains(
            response,
            "Imagen de la opción Opción visual",
        )

    def test_opcion_sin_imagen_no_genera_etiqueta_de_imagen(self):
        response = self.client.get(
            self.votacion.get_absolute_url()
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            "js-option-image",
        )

    def test_formulario_categoria_declara_multipart(self):
        from django.contrib.auth import get_user_model
        from django.urls import reverse

        usuario = get_user_model().objects.create_superuser(
            username="admin_imagen_categoria",
            email="admin-categoria@example.com",
            password="Temporal-2026",
        )

        self.client.force_login(usuario)

        response = self.client.get(
            reverse("elecciones:categoria_editar", args=[self.categoria.pk])
        )

        self.assertContains(
            response,
            'enctype="multipart/form-data"',
        )
        self.assertContains(
            response,
            "Imagen actual",
            count=0,
        )

    def test_formulario_votacion_declara_multipart(self):
        from django.contrib.auth import get_user_model
        from django.urls import reverse

        usuario = get_user_model().objects.create_superuser(
            username="admin_imagen_votacion",
            email="admin-votacion@example.com",
            password="Temporal-2026",
        )

        self.client.force_login(usuario)

        response = self.client.get(
            reverse("elecciones:votacion_editar", args=[self.votacion.pk])
        )

        self.assertContains(
            response,
            'enctype="multipart/form-data"',
        )
        self.assertContains(
            response,
            "Formatos permitidos",
        )

    def test_imagen_es_opcional(self):
        self.assertFalse(
            bool(self.categoria.imagen)
        )
        self.assertFalse(
            bool(self.votacion.imagen)
        )
        self.assertFalse(
            bool(self.opcion.imagen)
        )
