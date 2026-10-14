from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from elecciones.models import Categoria, Edicion, Festival, Opcion, TipoVotacion, Votacion

class Command(BaseCommand):
    help = "Carga datos demostrativos configurables"
    def handle(self, *args, **options):
        festival,_=Festival.objects.get_or_create(nombre="Festival de la Leyenda Vallenata", defaults={"descripcion":"Festival configurable"})
        edicion,_=Edicion.objects.get_or_create(festival=festival, anio=2027, defaults={"nombre":"Festival de la Leyenda Vallenata 2027","fecha_inicio":"2027-04-26","fecha_fin":"2027-05-02","estado":Edicion.Estado.ACTIVA})
        categoria,_=Categoria.objects.get_or_create(edicion=edicion,nombre="Categoría demostrativa",defaults={"descripcion":"Categoría creada desde datos configurables.","reglas":"Reglas pendientes de validación institucional.","estado":"ACTIVO","visible_publicamente":True})
        tipo,_=TipoVotacion.objects.get_or_create(nombre="Participación del público",defaults={"descripcion":"Votación demostrativa del público."})
        now=timezone.now()
        votacion,_=Votacion.objects.get_or_create(slug="votacion-demostrativa-2027",defaults={"categoria":categoria,"tipo":tipo,"nombre":"Votación demostrativa 2027","descripcion":"Prueba del núcleo configurable MVT.","fecha_apertura":now-timedelta(days=1),"fecha_cierre":now+timedelta(days=7),"estado":Votacion.Estado.ABIERTA,"publicada":True})
        for i,nombre in enumerate(["Opción A","Opción B","Opción C"],1): Opcion.objects.get_or_create(votacion=votacion,nombre=nombre,defaults={"orden":i})
        self.stdout.write(self.style.SUCCESS("Datos demostrativos creados."))
