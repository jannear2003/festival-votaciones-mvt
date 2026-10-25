import re

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(
    EMAIL_BACKEND=(
        "django.core.mail.backends.locmem.EmailBackend"
    ),
)
class RecuperacionPasswordTests(TestCase):
    password = "Clave-Actual-Segura-2026"
    new_password = "Clave-Nueva-Segura-2026"

    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="usuario_recuperacion",
            email="recuperacion@example.com",
            password=cls.password,
            is_active=True,
        )

    def setUp(self):
        self.login_url = reverse("login")
        self.solicitud_url = reverse("password_reset")
        self.solicitud_enviada_url = reverse(
            "password_reset_done"
        )
        self.completada_url = reverse(
            "password_reset_complete"
        )

    def solicitar_recuperacion(self):
        return self.client.post(
            self.solicitud_url,
            {
                "email": self.usuario.email,
            },
        )

    def obtener_enlace(self):
        self.solicitar_recuperacion()

        self.assertEqual(len(mail.outbox), 1)

        coincidencia = re.search(
            r"https?://[^\s]+/cuentas/reset/[^\s]+/[^\s]+/",
            mail.outbox[0].body,
        )

        self.assertIsNotNone(coincidencia)

        enlace = coincidencia.group(0)

        return enlace.replace(
            "http://testserver",
            "",
        ).replace(
            "https://testserver",
            "",
        )

    def test_login_muestra_enlace_de_recuperacion(self):
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "¿Olvidaste tu contraseña?",
        )
        self.assertContains(
            response,
            self.solicitud_url,
        )

    def test_formulario_de_solicitud_responde(self):
        response = self.client.get(self.solicitud_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "registration/password_reset_form.html",
        )
        self.assertContains(
            response,
            "Recuperar contraseña",
        )
        self.assertContains(
            response,
            'name="email"',
        )

    def test_correo_registrado_genera_mensaje(self):
        response = self.solicitar_recuperacion()

        self.assertRedirects(
            response,
            self.solicitud_enviada_url,
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].to,
            [self.usuario.email],
        )
        self.assertIn(
            "/cuentas/reset/",
            mail.outbox[0].body,
        )

    def test_correo_inexistente_no_revela_la_cuenta(self):
        response = self.client.post(
            self.solicitud_url,
            {
                "email": "cuenta-inexistente@example.com",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Si existe una cuenta activa",
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_respuesta_visible_es_neutral(self):
        existente = self.client.post(
            self.solicitud_url,
            {
                "email": self.usuario.email,
            },
            follow=True,
        )

        mail.outbox.clear()

        inexistente = self.client.post(
            self.solicitud_url,
            {
                "email": "no-registrado@example.com",
            },
            follow=True,
        )

        mensaje = "Si existe una cuenta activa"

        self.assertContains(existente, mensaje)
        self.assertContains(inexistente, mensaje)

    def test_token_manipulado_no_permite_cambio(self):
        enlace = self.obtener_enlace()
        partes = enlace.rstrip("/").split("/")
        partes[-1] = "token-invalido"
        enlace_invalido = "/".join(partes) + "/"

        response = self.client.get(enlace_invalido)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "El enlace no es válido",
        )

    def test_cambio_exitoso_actualiza_la_contrasena(self):
        enlace = self.obtener_enlace()

        response = self.client.get(enlace)

        self.assertEqual(response.status_code, 302)

        confirmacion_url = response["Location"]

        response = self.client.post(
            confirmacion_url,
            {
                "new_password1": self.new_password,
                "new_password2": self.new_password,
            },
        )

        self.assertRedirects(
            response,
            self.completada_url,
        )

        self.usuario.refresh_from_db()

        self.assertFalse(
            self.usuario.check_password(self.password),
        )
        self.assertTrue(
            self.usuario.check_password(self.new_password),
        )

    def test_contrasenas_diferentes_son_rechazadas(self):
        enlace = self.obtener_enlace()
        response = self.client.get(enlace)
        confirmacion_url = response["Location"]

        response = self.client.post(
            confirmacion_url,
            {
                "new_password1": self.new_password,
                "new_password2": "Otra-Clave-Segura-2026",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Los dos campos de contraseña no coinciden",
        )

        self.usuario.refresh_from_db()

        self.assertTrue(
            self.usuario.check_password(self.password),
        )

    def test_enlace_utilizado_no_puede_reutilizarse(self):
        enlace = self.obtener_enlace()

        primera_apertura = self.client.get(enlace)
        confirmacion_url = primera_apertura["Location"]

        self.client.post(
            confirmacion_url,
            {
                "new_password1": self.new_password,
                "new_password2": self.new_password,
            },
        )

        reutilizacion = self.client.get(enlace)

        self.assertEqual(reutilizacion.status_code, 200)
        self.assertContains(
            reutilizacion,
            "El enlace no es válido",
        )

    def test_usuario_puede_ingresar_con_nueva_contrasena(self):
        enlace = self.obtener_enlace()
        response = self.client.get(enlace)
        confirmacion_url = response["Location"]

        self.client.post(
            confirmacion_url,
            {
                "new_password1": self.new_password,
                "new_password2": self.new_password,
            },
        )

        ingreso_anterior = self.client.post(
            self.login_url,
            {
                "username": self.usuario.username,
                "password": self.password,
            },
        )

        self.assertEqual(ingreso_anterior.status_code, 200)

        ingreso_nuevo = self.client.post(
            self.login_url,
            {
                "username": self.usuario.username,
                "password": self.new_password,
            },
        )

        self.assertEqual(ingreso_nuevo.status_code, 302)