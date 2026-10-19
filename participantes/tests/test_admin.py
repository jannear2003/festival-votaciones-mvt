from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from participantes.admin import ParticipanteAdmin
from participantes.models import Participante


class ParticipanteAdminConfigurationTests(TestCase):
    def setUp(self):
        modelo_usuario = get_user_model()

        self.superusuario = modelo_usuario.objects.create_superuser(
            username="administrador_participantes",
            email="administrador@example.com",
            password="ClaveSeguraAdmin123!",
        )

        self.responsable = modelo_usuario.objects.create_user(
            username="responsable_admin",
            email="responsable.admin@example.com",
            password="ClaveSeguraResponsable123!",
        )

        self.participante = Participante.objects.create(
            responsable=self.responsable,
            tipo=Participante.Tipo.INDIVIDUAL,
            nombre_artistico="Participante Administración",
            nombre_legal="Persona Sintética Administración",
            ciudad="Valledupar",
            departamento="Cesar",
            pais="Colombia",
        )

    def test_modelo_esta_registrado_en_admin(self):
        self.assertTrue(
            admin.site.is_registered(Participante)
        )

    def test_modelo_utiliza_participante_admin(self):
        administrador = admin.site._registry[Participante]

        self.assertIsInstance(
            administrador,
            ParticipanteAdmin,
        )

    def test_listado_requiere_autenticacion(self):
        url = reverse(
            "admin:participantes_participante_changelist"
        )

        respuesta = self.client.get(url)

        self.assertEqual(
            respuesta.status_code,
            302,
        )
        self.assertIn(
            reverse("admin:login"),
            respuesta.url,
        )

    def test_superusuario_accede_al_listado(self):
        self.client.force_login(self.superusuario)

        url = reverse(
            "admin:participantes_participante_changelist"
        )

        respuesta = self.client.get(url)

        self.assertEqual(
            respuesta.status_code,
            200,
        )
        self.assertContains(
            respuesta,
            self.participante.nombre_artistico,
        )

    def test_superusuario_accede_al_formulario_de_creacion(self):
        self.client.force_login(self.superusuario)

        url = reverse(
            "admin:participantes_participante_add"
        )

        respuesta = self.client.get(url)

        self.assertEqual(
            respuesta.status_code,
            200,
        )
        self.assertContains(
            respuesta,
            "Identificación del participante",
        )
        self.assertContains(
            respuesta,
            "Información de contacto",
        )
        self.assertContains(
            respuesta,
            "Perfil artístico",
        )

    def test_superusuario_accede_al_formulario_de_edicion(self):
        self.client.force_login(self.superusuario)

        url = reverse(
            "admin:participantes_participante_change",
            args=[
                self.participante.pk,
            ],
        )

        respuesta = self.client.get(url)

        self.assertEqual(
            respuesta.status_code,
            200,
        )
        self.assertContains(
            respuesta,
            self.participante.nombre_artistico,
        )

    def test_busqueda_encuentra_participante(self):
        self.client.force_login(self.superusuario)

        url = reverse(
            "admin:participantes_participante_changelist"
        )

        respuesta = self.client.get(
            url,
            {
                "q": "Participante Administración",
            },
        )

        self.assertEqual(
            respuesta.status_code,
            200,
        )
        self.assertContains(
            respuesta,
            self.participante.nombre_artistico,
        )

    def test_filtro_por_tipo_funciona(self):
        self.client.force_login(self.superusuario)

        url = reverse(
            "admin:participantes_participante_changelist"
        )

        respuesta = self.client.get(
            url,
            {
                "tipo__exact": Participante.Tipo.INDIVIDUAL,
            },
        )

        self.assertEqual(
            respuesta.status_code,
            200,
        )
        self.assertContains(
            respuesta,
            self.participante.nombre_artistico,
        )

    def test_campos_de_auditoria_son_solo_lectura(self):
        administrador = admin.site._registry[Participante]

        self.assertIn(
            "creado_en",
            administrador.readonly_fields,
        )
        self.assertIn(
            "actualizado_en",
            administrador.readonly_fields,
        )

    def test_responsable_utiliza_autocompletado(self):
        administrador = admin.site._registry[Participante]

        self.assertIn(
            "responsable",
            administrador.autocomplete_fields,
        )
