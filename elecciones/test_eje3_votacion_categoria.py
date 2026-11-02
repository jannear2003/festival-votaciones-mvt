from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
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


class CasosPruebaEje3Tests(TestCase):
    password = "Temporal-Eje3-2026"

    @classmethod
    def setUpTestData(cls):
        ahora = timezone.now()

        cls.festival = Festival.objects.create(
            nombre="Festival Eje 3",
            descripcion="Datos controlados para la tercera entrega",
        )

        cls.edicion = Edicion.objects.create(
            festival=cls.festival,
            nombre="Edición Eje 3",
            anio=2030,
            fecha_inicio=ahora.date(),
            fecha_fin=(ahora + timedelta(days=10)).date(),
            estado=Edicion.Estado.ACTIVA,
        )

        cls.categoria_uno = Categoria.objects.create(
            edicion=cls.edicion,
            nombre="Categoría principal",
            descripcion="Categoría con dos subeventos",
            estado=EstadoBase.ACTIVO,
            visible_publicamente=True,
            orden=1,
        )

        cls.categoria_dos = Categoria.objects.create(
            edicion=cls.edicion,
            nombre="Categoría alternativa",
            descripcion="Categoría diferente",
            estado=EstadoBase.ACTIVO,
            visible_publicamente=True,
            orden=2,
        )

        cls.categoria_cerrada = Categoria.objects.create(
            edicion=cls.edicion,
            nombre="Categoría no habilitada",
            descripcion="Categoría inactiva",
            estado=EstadoBase.INACTIVO,
            visible_publicamente=False,
            orden=3,
        )

        cls.tipo = TipoVotacion.objects.create(
            nombre="Tipo Eje 3",
            descripcion="Tipo empleado en las pruebas",
            activo=True,
        )

        cls.votacion_uno = Votacion.objects.create(
            categoria=cls.categoria_uno,
            tipo=cls.tipo,
            nombre="Subevento uno",
            slug="eje3-subevento-uno",
            descripcion="Primera votación de la misma categoría",
            fecha_apertura=ahora - timedelta(hours=1),
            fecha_cierre=ahora + timedelta(hours=5),
            estado=Votacion.Estado.ABIERTA,
            publicada=True,
        )

        cls.votacion_dos = Votacion.objects.create(
            categoria=cls.categoria_uno,
            tipo=cls.tipo,
            nombre="Subevento dos",
            slug="eje3-subevento-dos",
            descripcion="Segunda votación de la misma categoría",
            fecha_apertura=ahora - timedelta(hours=1),
            fecha_cierre=ahora + timedelta(hours=5),
            estado=Votacion.Estado.ABIERTA,
            publicada=True,
        )

        cls.votacion_otra_categoria = Votacion.objects.create(
            categoria=cls.categoria_dos,
            tipo=cls.tipo,
            nombre="Votación de otra categoría",
            slug="eje3-otra-categoria",
            descripcion="Proceso permitido para el mismo usuario",
            fecha_apertura=ahora - timedelta(hours=1),
            fecha_cierre=ahora + timedelta(hours=5),
            estado=Votacion.Estado.ABIERTA,
            publicada=True,
        )

        cls.votacion_no_habilitada = Votacion.objects.create(
            categoria=cls.categoria_cerrada,
            tipo=cls.tipo,
            nombre="Votación no habilitada",
            slug="eje3-no-habilitada",
            descripcion="Proceso que debe ser rechazado",
            fecha_apertura=ahora - timedelta(hours=1),
            fecha_cierre=ahora + timedelta(hours=5),
            estado=Votacion.Estado.ABIERTA,
            publicada=False,
        )

        cls.opcion_uno = Opcion.objects.create(
            votacion=cls.votacion_uno,
            nombre="Opción subevento uno",
            activa=True,
            orden=1,
        )

        cls.opcion_dos = Opcion.objects.create(
            votacion=cls.votacion_dos,
            nombre="Opción subevento dos",
            activa=True,
            orden=1,
        )

        cls.opcion_otra_categoria = Opcion.objects.create(
            votacion=cls.votacion_otra_categoria,
            nombre="Opción categoría alternativa",
            activa=True,
            orden=1,
        )

        cls.opcion_no_habilitada = Opcion.objects.create(
            votacion=cls.votacion_no_habilitada,
            nombre="Opción no habilitada",
            activa=True,
            orden=1,
        )

        User = get_user_model()

        cls.usuario = User.objects.create_user(
            username="usuario_eje3",
            email="usuario.eje3@example.com",
            password=cls.password,
        )

        cls.otro_usuario = User.objects.create_user(
            username="otro_usuario_eje3",
            email="otro.usuario.eje3@example.com",
            password=cls.password,
        )

    def emitir_voto(self, votacion, opcion):
        participar_url = reverse(
            "elecciones:participar",
            kwargs={"slug": votacion.slug},
        )
        revisar_url = reverse(
            "elecciones:revisar_voto",
            kwargs={"slug": votacion.slug},
        )
        confirmar_url = reverse(
            "elecciones:confirmar_voto",
            kwargs={"slug": votacion.slug},
        )
        comprobante_url = reverse(
            "elecciones:comprobante_voto",
            kwargs={"slug": votacion.slug},
        )

        response = self.client.post(
            participar_url,
            {"opcion": opcion.pk},
        )
        self.assertRedirects(response, revisar_url)

        response = self.client.post(confirmar_url)
        self.assertRedirects(response, comprobante_url)

    def test_cp01_voto_valido_se_registra_en_mysql(self):
        self.client.force_login(self.usuario)

        self.emitir_voto(
            self.votacion_uno,
            self.opcion_uno,
        )

        participacion = Participacion.objects.get(
            usuario=self.usuario,
            categoria=self.categoria_uno,
            edicion=self.edicion,
        )

        self.assertEqual(
            participacion.votacion,
            self.votacion_uno,
        )
        self.assertEqual(
            participacion.estado,
            Participacion.Estado.CONFIRMADA,
        )
        self.assertTrue(
            Voto.objects.filter(
                participacion=participacion,
                votacion=self.votacion_uno,
                opcion=self.opcion_uno,
            ).exists()
        )

    def test_cp02_no_permite_segundo_voto_en_misma_categoria(self):
        self.client.force_login(self.usuario)

        self.emitir_voto(
            self.votacion_uno,
            self.opcion_uno,
        )

        response = self.client.get(
            reverse(
                "elecciones:participar",
                kwargs={"slug": self.votacion_dos.slug},
            )
        )

        self.assertRedirects(
            response,
            reverse(
                "elecciones:participacion_duplicada",
                kwargs={"slug": self.votacion_dos.slug},
            ),
            fetch_redirect_response=False,
        )

        self.assertEqual(
            Participacion.objects.filter(
                usuario=self.usuario,
                categoria=self.categoria_uno,
                edicion=self.edicion,
            ).count(),
            1,
        )
        self.assertEqual(
            Voto.objects.filter(
                participacion__usuario=self.usuario,
                participacion__categoria=self.categoria_uno,
                participacion__edicion=self.edicion,
            ).count(),
            1,
        )

    def test_cp02_mysql_rechaza_duplicado_en_otro_subevento(self):
        Participacion.objects.create(
            votacion=self.votacion_uno,
            categoria=self.categoria_uno,
            edicion=self.edicion,
            usuario=self.usuario,
            referencia="EJE3-UNICO-001",
            clave_sesion="eje3-sesion-uno",
            estado=Participacion.Estado.CONFIRMADA,
            confirmada_en=timezone.now(),
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Participacion.objects.bulk_create(
                    [
                        Participacion(
                            votacion=self.votacion_dos,
                            categoria=self.categoria_uno,
                            edicion=self.edicion,
                            usuario=self.usuario,
                            referencia="EJE3-DUPLICADO-002",
                            clave_sesion="eje3-sesion-dos",
                            estado=Participacion.Estado.CONFIRMADA,
                            confirmada_en=timezone.now(),
                        )
                    ]
                )

        self.assertEqual(
            Participacion.objects.filter(
                usuario=self.usuario,
                categoria=self.categoria_uno,
                edicion=self.edicion,
            ).count(),
            1,
        )

    def test_cp03_permite_votar_en_categoria_diferente(self):
        self.client.force_login(self.usuario)

        self.emitir_voto(
            self.votacion_uno,
            self.opcion_uno,
        )
        self.emitir_voto(
            self.votacion_otra_categoria,
            self.opcion_otra_categoria,
        )

        self.assertEqual(
            Participacion.objects.filter(
                usuario=self.usuario,
                edicion=self.edicion,
                estado=Participacion.Estado.CONFIRMADA,
            ).count(),
            2,
        )

        categorias = set(
            Participacion.objects.filter(
                usuario=self.usuario,
                edicion=self.edicion,
            ).values_list("categoria_id", flat=True)
        )

        self.assertEqual(
            categorias,
            {
                self.categoria_uno.pk,
                self.categoria_dos.pk,
            },
        )

    def test_cp04_visitante_no_puede_ingresar_al_flujo(self):
        url = reverse(
            "elecciones:participar",
            kwargs={"slug": self.votacion_uno.slug},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_cp05_categoria_no_habilitada_rechaza_operacion(self):
        self.client.force_login(self.usuario)

        response = self.client.get(
            reverse(
                "elecciones:participar",
                kwargs={
                    "slug": self.votacion_no_habilitada.slug,
                },
            )
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Participacion.objects.count(), 0)
        self.assertEqual(Voto.objects.count(), 0)

    def test_cp06_opcion_de_otra_categoria_es_rechazada(self):
        self.client.force_login(self.usuario)

        response = self.client.post(
            reverse(
                "elecciones:participar",
                kwargs={"slug": self.votacion_uno.slug},
            ),
            {
                "opcion": self.opcion_otra_categoria.pk,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "opcion",
            (
                "Escoja una opción válida. "
                "Esa opción no está entre las disponibles."
            ),
        )
        self.assertEqual(Participacion.objects.count(), 0)
        self.assertEqual(Voto.objects.count(), 0)

    def test_cp07_historial_muestra_las_categorias_votadas(self):
        self.client.force_login(self.usuario)

        self.emitir_voto(
            self.votacion_uno,
            self.opcion_uno,
        )
        self.emitir_voto(
            self.votacion_otra_categoria,
            self.opcion_otra_categoria,
        )

        response = self.client.get(
            reverse("elecciones:mis_participaciones")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            self.categoria_uno.nombre,
        )
        self.assertContains(
            response,
            self.categoria_dos.nombre,
        )
        self.assertContains(
            response,
            self.edicion.nombre,
        )

    def test_cp08_registro_persistido_es_consultable(self):
        self.client.force_login(self.usuario)

        self.emitir_voto(
            self.votacion_uno,
            self.opcion_uno,
        )

        participacion = (
            Participacion.objects.select_related(
                "usuario",
                "edicion",
                "categoria",
                "votacion",
            )
            .get(
                usuario=self.usuario,
                categoria=self.categoria_uno,
                edicion=self.edicion,
            )
        )

        voto = Voto.objects.select_related(
            "participacion",
            "votacion",
            "opcion",
        ).get(participacion=participacion)

        self.assertEqual(
            voto.votacion,
            self.votacion_uno,
        )
        self.assertEqual(
            voto.opcion,
            self.opcion_uno,
        )
        self.assertEqual(
            participacion.usuario,
            self.usuario,
        )
