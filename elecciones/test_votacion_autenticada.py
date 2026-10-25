from datetime import timedelta
from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
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


class VotacionAutenticadaTests(TestCase):
    password = "Temporal-Pruebas-2026"

    @classmethod
    def setUpTestData(cls):
        ahora = timezone.now()

        cls.festival = Festival.objects.create(
            nombre="Festival de prueba",
            descripcion="Prueba de votación autenticada",
        )

        cls.edicion = Edicion.objects.create(
            festival=cls.festival,
            nombre="Edición de prueba",
            anio=2027,
            fecha_inicio=ahora.date(),
            fecha_fin=(ahora + timedelta(days=5)).date(),
            estado=EstadoBase.ACTIVO,
        )

        cls.categoria = Categoria.objects.create(
            edicion=cls.edicion,
            nombre="Categoría de prueba",
            descripcion="Categoría visible",
            estado=EstadoBase.ACTIVO,
            visible_publicamente=True,
            orden=1,
        )

        cls.tipo = TipoVotacion.objects.create(
            nombre="Favorito del público",
        )

        cls.votacion = Votacion.objects.create(
            categoria=cls.categoria,
            tipo=cls.tipo,
            nombre="Votación autenticada",
            slug="votacion-autenticada-prueba",
            descripcion="Votación disponible",
            fecha_apertura=ahora - timedelta(hours=1),
            fecha_cierre=ahora + timedelta(hours=2),
            estado=Votacion.Estado.ABIERTA,
            publicada=True,
        )

        cls.opcion = Opcion.objects.create(
            votacion=cls.votacion,
            nombre="Opción uno",
            descripcion="Primera alternativa",
            orden=1,
            activa=True,
        )

        cls.segunda_opcion = Opcion.objects.create(
            votacion=cls.votacion,
            nombre="Opción dos",
            descripcion="Segunda alternativa",
            orden=2,
            activa=True,
        )

        User = get_user_model()

        cls.usuario = User.objects.create_user(
            username="votante_uno",
            email="votante.uno@example.com",
            password=cls.password,
        )

        cls.otro_usuario = User.objects.create_user(
            username="votante_dos",
            email="votante.dos@example.com",
            password=cls.password,
        )

    def setUp(self):
        self.detalle_url = reverse(
            "elecciones:detalle",
            kwargs={"slug": self.votacion.slug},
        )
        self.participar_url = reverse(
            "elecciones:participar",
            kwargs={"slug": self.votacion.slug},
        )
        self.revisar_url = reverse(
            "elecciones:revisar_voto",
            kwargs={"slug": self.votacion.slug},
        )
        self.confirmar_url = reverse(
            "elecciones:confirmar_voto",
            kwargs={"slug": self.votacion.slug},
        )
        self.comprobante_url = reverse(
            "elecciones:comprobante_voto",
            kwargs={"slug": self.votacion.slug},
        )
        self.duplicada_url = reverse(
            "elecciones:participacion_duplicada",
            kwargs={"slug": self.votacion.slug},
        )

    def test_visitante_puede_ver_detalle_y_opciones(self):
        response = self.client.get(self.detalle_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.votacion.nombre)
        self.assertContains(response, self.opcion.nombre)
        self.assertContains(response, self.segunda_opcion.nombre)

    def test_visitante_ve_invitacion_para_autenticarse(self):
        response = self.client.get(self.detalle_url)

        self.assertContains(
            response,
            "Para participar debes registrarte o iniciar sesión.",
        )
        self.assertContains(
            response,
            "Iniciar sesión para votar",
        )
        self.assertContains(
            response,
            "Crear cuenta",
        )

    def test_visitante_no_ve_el_formulario_de_voto(self):
        response = self.client.get(self.detalle_url)

        self.assertNotContains(
            response,
            "Revisar selección",
        )

    def test_visitante_es_redirigido_al_login(self):
        response = self.client.get(self.participar_url)

        self.assertEqual(response.status_code, 302)

        destino = response["Location"]
        query = parse_qs(urlparse(destino).query)

        self.assertEqual(
            urlparse(destino).path,
            reverse("login"),
        )
        self.assertEqual(
            query.get("next"),
            [self.participar_url],
        )

    def test_todas_las_rutas_del_voto_exigen_login(self):
        casos = (
            ("get", self.participar_url),
            ("get", self.revisar_url),
            ("post", self.confirmar_url),
            ("get", self.comprobante_url),
            ("get", self.duplicada_url),
        )

        for metodo, url in casos:
            with self.subTest(url=url):
                response = getattr(
                    self.client,
                    metodo,
                )(url)

                self.assertEqual(response.status_code, 302)
                self.assertEqual(
                    urlparse(response["Location"]).path,
                    reverse("login"),
                )

    def test_usuario_autenticado_accede_al_formulario(self):
        self.client.force_login(self.usuario)

        response = self.client.get(self.participar_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Seleccione una opción")
        self.assertContains(response, self.opcion.nombre)

    def test_voto_confirmado_se_asocia_al_usuario(self):
        self.client.force_login(self.usuario)

        response = self.client.post(
            self.participar_url,
            {"opcion": self.opcion.pk},
        )

        self.assertRedirects(
            response,
            self.revisar_url,
        )

        response = self.client.post(
            self.confirmar_url,
        )

        self.assertRedirects(
            response,
            self.comprobante_url,
        )

        participacion = Participacion.objects.get(
            votacion=self.votacion,
            usuario=self.usuario,
        )

        self.assertEqual(
            participacion.estado,
            Participacion.Estado.CONFIRMADA,
        )
        self.assertTrue(
            Voto.objects.filter(
                participacion=participacion,
                opcion=self.opcion,
            ).exists()
        )

    def test_usuario_no_puede_votar_dos_veces(self):
        participacion = Participacion.objects.create(
            votacion=self.votacion,
            usuario=self.usuario,
            referencia="VOT-USUARIO-DUPLICADO",
            clave_sesion="sesion-historica-usuario",
            estado=Participacion.Estado.CONFIRMADA,
            confirmada_en=timezone.now(),
        )

        Voto.objects.create(
            participacion=participacion,
            votacion=self.votacion,
            opcion=self.opcion,
        )

        self.client.force_login(self.usuario)

        response = self.client.get(
            self.participar_url,
        )

        self.assertRedirects(
            response,
            self.duplicada_url,
            fetch_redirect_response=False,
        )

    def test_cambiar_de_sesion_no_permite_otro_voto(self):
        participacion = Participacion.objects.create(
            votacion=self.votacion,
            usuario=self.usuario,
            referencia="VOT-OTRA-SESION",
            clave_sesion="primera-sesion",
            estado=Participacion.Estado.CONFIRMADA,
            confirmada_en=timezone.now(),
        )

        Voto.objects.create(
            participacion=participacion,
            votacion=self.votacion,
            opcion=self.opcion,
        )

        otro_navegador = Client()
        otro_navegador.force_login(self.usuario)

        response = otro_navegador.get(
            self.participar_url,
        )

        self.assertRedirects(
            response,
            self.duplicada_url,
            fetch_redirect_response=False,
        )

    def test_otro_usuario_si_puede_participar(self):
        Participacion.objects.create(
            votacion=self.votacion,
            usuario=self.usuario,
            referencia="VOT-PRIMER-USUARIO",
            clave_sesion="primera-cuenta",
            estado=Participacion.Estado.CONFIRMADA,
            confirmada_en=timezone.now(),
        )

        self.client.force_login(
            self.otro_usuario,
        )

        response = self.client.get(
            self.participar_url,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Seleccione una opción")

    def test_comprobante_solo_pertenece_al_usuario(self):
        participacion = Participacion.objects.create(
            votacion=self.votacion,
            usuario=self.usuario,
            referencia="VOT-COMPROBANTE-PRIVADO",
            clave_sesion="sesion-comprobante",
            estado=Participacion.Estado.CONFIRMADA,
            confirmada_en=timezone.now(),
        )

        self.client.force_login(
            self.otro_usuario,
        )

        session = self.client.session
        session[
            f"referencia_votacion_{self.votacion.pk}"
        ] = participacion.referencia
        session.save()

        response = self.client.get(
            self.comprobante_url,
        )

        self.assertEqual(response.status_code, 404)

    def test_pagina_duplicada_requiere_participacion_real(self):
        self.client.force_login(self.usuario)

        response = self.client.get(
            self.duplicada_url,
        )

        self.assertRedirects(
            response,
            self.participar_url,
            fetch_redirect_response=False,
        )

    def test_participacion_historica_sin_usuario_es_valida(self):
        participacion = Participacion.objects.create(
            votacion=self.votacion,
            usuario=None,
            referencia="VOT-HISTORICA-SIN-USUARIO",
            clave_sesion="sesion-historica-sin-usuario",
            estado=Participacion.Estado.CONFIRMADA,
            confirmada_en=timezone.now(),
        )

        self.assertIsNone(participacion.usuario)
