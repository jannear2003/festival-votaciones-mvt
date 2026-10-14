from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Categoria, Edicion, Festival, Opcion, TipoVotacion, Votacion

class NucleoConfigurableTests(TestCase):
    def setUp(self):
        self.festival=Festival.objects.create(nombre="Festival")
        self.edicion=Edicion.objects.create(festival=self.festival,nombre="Edición 2027",anio=2027,fecha_inicio=date(2027,1,1),fecha_fin=date(2027,12,31),estado=Edicion.Estado.ACTIVA)
        self.categoria=Categoria.objects.create(edicion=self.edicion,nombre="Categoría libre",estado="ACTIVO",visible_publicamente=True)
        self.tipo=TipoVotacion.objects.create(nombre="Público")
        self.votacion=Votacion.objects.create(categoria=self.categoria,tipo=self.tipo,nombre="Votación 1",slug="votacion-1",descripcion="Demo",fecha_apertura=timezone.now(),fecha_cierre=timezone.now()+timedelta(days=1),estado=Votacion.Estado.ABIERTA,publicada=True)
        Opcion.objects.create(votacion=self.votacion,nombre="Opción 1")

    def test_categoria_puede_repetirse_en_otra_edicion(self):
        otra=Edicion.objects.create(festival=self.festival,nombre="Edición 2028",anio=2028,fecha_inicio=date(2028,1,1),fecha_fin=date(2028,12,31),estado=Edicion.Estado.CONFIGURACION)
        Categoria.objects.create(edicion=otra,nombre="Categoría libre")
        self.assertEqual(Categoria.objects.filter(nombre="Categoría libre").count(),2)

    def test_categoria_visible_debe_estar_activa(self):
        categoria=Categoria(edicion=self.edicion,nombre="Inválida",estado="BORRADOR",visible_publicamente=True)
        with self.assertRaises(ValidationError): categoria.full_clean()

    def test_inicio_muestra_votacion_publicada(self):
        response=self.client.get(reverse("elecciones:inicio"))
        self.assertContains(response,"Votación 1")

    def test_detalle_muestra_opcion(self):
        response=self.client.get(self.votacion.get_absolute_url())
        self.assertContains(response,"Opción 1")
