from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse


class RegistroUsuarioTests(TestCase):
    def setUp(self):
        self.url = reverse("elecciones:registro")
        self.login_url = reverse("login")
        self.password = "ClaveFestivalMuySegura!2026"
        self.datos_validos = {
            "username": "usuario_nuevo",
            "first_name": "Usuario",
            "last_name": "Academico",
            "email": "usuario@example.com",
            "password1": self.password,
            "password2": self.password,
        }

    def test_formulario_registro_responde_y_usa_plantilla(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/registro.html")
        self.assertContains(response, "Crear cuenta")

    def test_registro_valido_crea_usuario_y_redirige_al_login(self):
        response = self.client.post(self.url, self.datos_validos)
        self.assertRedirects(response, self.login_url)

        user = get_user_model().objects.get(username="usuario_nuevo")
        self.assertEqual(user.email, "usuario@example.com")
        self.assertEqual(user.first_name, "Usuario")
        self.assertEqual(user.last_name, "Academico")
        self.assertTrue(user.check_password(self.password))
        self.assertNotEqual(user.password, self.password)

    def test_nombre_de_usuario_duplicado_es_rechazado(self):
        get_user_model().objects.create_user(
            username="usuario_nuevo",
            email="otro@example.com",
            password=self.password,
        )
        response = self.client.post(self.url, self.datos_validos)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            get_user_model().objects.filter(username="usuario_nuevo").count(),
            1,
        )
        self.assertFormError(
            response.context["form"],
            "username",
            "Ya existe un usuario con este nombre.",
        )

    def test_correo_duplicado_es_rechazado(self):
        get_user_model().objects.create_user(
            username="usuario_existente",
            email="usuario@example.com",
            password=self.password,
        )
        response = self.client.post(self.url, self.datos_validos)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "email",
            "Ya existe una cuenta registrada con este correo.",
        )
        self.assertFalse(
            get_user_model().objects.filter(username="usuario_nuevo").exists()
        )

    def test_contrasenas_diferentes_son_rechazadas(self):
        datos = self.datos_validos.copy()
        datos["password2"] = "UnaClaveDiferente!2026"
        response = self.client.post(self.url, datos)
        self.assertEqual(response.status_code, 200)
        self.assertIn("password2", response.context["form"].errors)
        self.assertFalse(
            get_user_model().objects.filter(username="usuario_nuevo").exists()
        )

    def test_usuario_autenticado_no_accede_al_registro(self):
        user = get_user_model().objects.create_user(
            username="usuario_autenticado",
            email="autenticado@example.com",
            password=self.password,
        )
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("elecciones:inicio"))

    def test_usuario_registrado_puede_iniciar_y_cerrar_sesion(self):
        self.client.post(self.url, self.datos_validos)
        login_ok = self.client.login(
            username="usuario_nuevo",
            password=self.password,
        )
        self.assertTrue(login_ok)

        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("elecciones:inicio"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_usuario_publico_no_accede_al_panel_administrativo(self):
        user = get_user_model().objects.create_user(
            username="usuario_publico",
            email="publico@example.com",
            password=self.password,
        )
        self.client.force_login(user)
        response = self.client.get(reverse("elecciones:panel"))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "403.html")

    def test_usuario_publico_no_ve_enlaces_administrativos(self):
        user = get_user_model().objects.create_user(
            username="usuario_publico",
            email="publico@example.com",
            password=self.password,
        )
        self.client.force_login(user)
        response = self.client.get(reverse("elecciones:inicio"))
        self.assertNotContains(response, ">Panel<")
        self.assertNotContains(response, "Django Admin")
        self.assertContains(response, "Salir")

    def test_superusuario_accede_al_panel_y_ve_enlaces(self):
        user = get_user_model().objects.create_superuser(
            username="administrador_prueba",
            email="admin@example.com",
            password=self.password,
        )
        self.client.force_login(user)
        response = self.client.get(reverse("elecciones:panel"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ">Panel<", html=False)
        self.assertContains(response, "Django Admin")

    def test_usuario_publico_no_accede_a_django_admin(self):
        user = get_user_model().objects.create_user(
            username="usuario_publico",
            email="publico@example.com",
            password=self.password,
        )
        self.client.force_login(user)
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("admin:login"), response.url)

    def test_login_usuario_publico_redirige_al_portal(self):
        get_user_model().objects.create_user(
            username="publico_login",
            email="publico.login@example.com",
            password=self.password,
        )
        response = self.client.post(
            self.login_url,
            {"username": "publico_login", "password": self.password},
        )
        self.assertRedirects(response, reverse("elecciones:inicio"))

    def test_login_superusuario_redirige_al_panel(self):
        get_user_model().objects.create_superuser(
            username="super_login",
            email="super.login@example.com",
            password=self.password,
        )
        response = self.client.post(
            self.login_url,
            {"username": "super_login", "password": self.password},
        )
        self.assertRedirects(response, reverse("elecciones:panel"))

    def test_login_usuario_con_grupo_administrativo_redirige_al_panel(self):
        user = get_user_model().objects.create_user(
            username="configurador_login",
            email="configurador.login@example.com",
            password=self.password,
        )
        group = Group.objects.create(name="Configurador")
        user.groups.add(group)

        response = self.client.post(
            self.login_url,
            {"username": "configurador_login", "password": self.password},
        )
        self.assertRedirects(response, reverse("elecciones:panel"))

    def test_login_respeta_next_para_ruta_publica_segura(self):
        get_user_model().objects.create_user(
            username="publico_next",
            email="publico.next@example.com",
            password=self.password,
        )
        destino = reverse("elecciones:inicio")
        response = self.client.post(
            f"{self.login_url}?next={destino}",
            {
                "username": "publico_next",
                "password": self.password,
                "next": destino,
            },
        )
        self.assertRedirects(response, destino)
