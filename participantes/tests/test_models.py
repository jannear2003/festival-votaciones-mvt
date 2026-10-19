from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from participantes.models import Participante


class ParticipanteModelTests(TestCase):
    def setUp(self):
        modelo_usuario = get_user_model()

        self.responsable = modelo_usuario.objects.create_user(
            username="responsable_demo",
            email="responsable@example.com",
            password="ClaveSeguraDemo123!",
        )

    def test_crear_participante_individual(self):
        participante = Participante.objects.create(
            responsable=self.responsable,
            tipo=Participante.Tipo.INDIVIDUAL,
            nombre_artistico="Acordeonista Demo",
            nombre_legal="Persona Sintética",
        )

        self.assertEqual(
            participante.tipo,
            Participante.Tipo.INDIVIDUAL,
        )
        self.assertEqual(
            participante.nombre_artistico,
            "Acordeonista Demo",
        )
        self.assertTrue(participante.activo)

    def test_crear_agrupacion_sin_nombre_legal(self):
        participante = Participante.objects.create(
            responsable=self.responsable,
            tipo=Participante.Tipo.AGRUPACION,
            nombre_artistico="Agrupación de Prueba",
        )

        participante.full_clean()

        self.assertEqual(
            participante.tipo,
            Participante.Tipo.AGRUPACION,
        )
        self.assertEqual(
            participante.nombre_legal,
            "",
        )

    def test_representacion_textual(self):
        participante = Participante.objects.create(
            responsable=self.responsable,
            tipo=Participante.Tipo.INDIVIDUAL,
            nombre_artistico="Participante Sintético",
            nombre_legal="Nombre Sintético",
        )

        self.assertEqual(
            str(participante),
            "Participante Sintético",
        )

    def test_pais_predeterminado(self):
        participante = Participante.objects.create(
            responsable=self.responsable,
            tipo=Participante.Tipo.INDIVIDUAL,
            nombre_artistico="Participante Colombia",
            nombre_legal="Nombre Colombia",
        )

        self.assertEqual(
            participante.pais,
            "Colombia",
        )

    def test_nombre_artistico_es_obligatorio(self):
        participante = Participante(
            responsable=self.responsable,
            tipo=Participante.Tipo.INDIVIDUAL,
            nombre_artistico="",
            nombre_legal="Nombre Sintético",
        )

        with self.assertRaises(ValidationError) as contexto:
            participante.full_clean()

        self.assertIn(
            "nombre_artistico",
            contexto.exception.message_dict,
        )

    def test_nombre_legal_es_obligatorio_para_individual(self):
        participante = Participante(
            responsable=self.responsable,
            tipo=Participante.Tipo.INDIVIDUAL,
            nombre_artistico="Participante sin nombre legal",
            nombre_legal="",
        )

        with self.assertRaises(ValidationError) as contexto:
            participante.full_clean()

        self.assertIn(
            "nombre_legal",
            contexto.exception.message_dict,
        )

    def test_no_permite_tipo_invalido(self):
        participante = Participante(
            responsable=self.responsable,
            tipo="TIPO_INEXISTENTE",
            nombre_artistico="Participante Inválido",
            nombre_legal="Nombre Sintético",
        )

        with self.assertRaises(ValidationError) as contexto:
            participante.full_clean()

        self.assertIn(
            "tipo",
            contexto.exception.message_dict,
        )

    def test_no_permite_duplicado_para_mismo_responsable(self):
        datos = {
            "responsable": self.responsable,
            "tipo": Participante.Tipo.INDIVIDUAL,
            "nombre_artistico": "Nombre Repetido",
            "nombre_legal": "Nombre Sintético",
        }

        Participante.objects.create(**datos)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Participante.objects.create(**datos)

    def test_permite_mismo_nombre_para_otro_responsable(self):
        modelo_usuario = get_user_model()

        otro_responsable = modelo_usuario.objects.create_user(
            username="otro_responsable",
            email="otro@example.com",
            password="ClaveSeguraDemo456!",
        )

        Participante.objects.create(
            responsable=self.responsable,
            tipo=Participante.Tipo.INDIVIDUAL,
            nombre_artistico="Nombre Compartido",
            nombre_legal="Primera Persona",
        )

        segundo = Participante.objects.create(
            responsable=otro_responsable,
            tipo=Participante.Tipo.INDIVIDUAL,
            nombre_artistico="Nombre Compartido",
            nombre_legal="Segunda Persona",
        )

        self.assertIsNotNone(segundo.pk)

    def test_permite_inactivar_sin_eliminar(self):
        participante = Participante.objects.create(
            responsable=self.responsable,
            tipo=Participante.Tipo.INDIVIDUAL,
            nombre_artistico="Participante Inactivo",
            nombre_legal="Nombre Sintético",
        )

        participante.activo = False
        participante.save(update_fields=["activo"])
        participante.refresh_from_db()

        self.assertFalse(participante.activo)
        self.assertTrue(
            Participante.objects.filter(
                pk=participante.pk,
            ).exists()
        )

    def test_fotografia_es_opcional(self):
        participante = Participante(
            responsable=self.responsable,
            tipo=Participante.Tipo.INDIVIDUAL,
            nombre_artistico="Participante sin fotografía",
            nombre_legal="Nombre Sintético",
        )

        participante.full_clean()
        participante.save()

        self.assertFalse(bool(participante.fotografia))
