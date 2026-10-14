from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class EstadoBase(models.TextChoices):
    BORRADOR = "BORRADOR", "Borrador"
    ACTIVO = "ACTIVO", "Activo"
    INACTIVO = "INACTIVO", "Inactivo"
    ARCHIVADO = "ARCHIVADO", "Archivado"


class Festival(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "festival"
        verbose_name_plural = "festivales"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Edicion(models.Model):
    class Estado(models.TextChoices):
        BORRADOR = "BORRADOR", "Borrador"
        CONFIGURACION = "CONFIGURACION", "En configuración"
        ACTIVA = "ACTIVA", "Activa"
        CERRADA = "CERRADA", "Cerrada"
        ARCHIVADA = "ARCHIVADA", "Archivada"

    festival = models.ForeignKey(Festival, on_delete=models.PROTECT, related_name="ediciones")
    nombre = models.CharField(max_length=150)
    anio = models.PositiveIntegerField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.BORRADOR)

    class Meta:
        verbose_name = "edición"
        verbose_name_plural = "ediciones"
        ordering = ["-anio", "nombre"]
        constraints = [models.UniqueConstraint(fields=["festival", "anio"], name="edicion_unica_por_festival_anio")]

    def clean(self):
        if self.fecha_fin and self.fecha_inicio and self.fecha_fin < self.fecha_inicio:
            raise ValidationError({"fecha_fin": "La fecha final no puede ser anterior a la fecha inicial."})

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    edicion = models.ForeignKey(Edicion, on_delete=models.PROTECT, related_name="categorias")
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    reglas = models.TextField(blank=True)
    orden = models.PositiveIntegerField(default=1)
    estado = models.CharField(max_length=15, choices=EstadoBase.choices, default=EstadoBase.BORRADOR)
    visible_publicamente = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["orden", "nombre"]
        constraints = [models.UniqueConstraint(fields=["edicion", "nombre"], name="categoria_nombre_unico_por_edicion")]

    def clean(self):
        if self.estado == EstadoBase.ACTIVO and self.edicion.estado not in {Edicion.Estado.CONFIGURACION, Edicion.Estado.ACTIVA}:
            raise ValidationError({"estado": "La categoría solo puede activarse en una edición en configuración o activa."})
        if self.visible_publicamente and self.estado != EstadoBase.ACTIVO:
            raise ValidationError({"visible_publicamente": "Solo una categoría activa puede ser visible públicamente."})

    def __str__(self):
        return f"{self.nombre} · {self.edicion.nombre}"


class TipoVotacion(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "tipo de votación"
        verbose_name_plural = "tipos de votación"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Votacion(models.Model):
    class Estado(models.TextChoices):
        BORRADOR = "BORRADOR", "Borrador"
        PROGRAMADA = "PROGRAMADA", "Programada"
        ABIERTA = "ABIERTA", "Abierta"
        CERRADA = "CERRADA", "Cerrada"
        CANCELADA = "CANCELADA", "Cancelada"

    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="votaciones")
    tipo = models.ForeignKey(TipoVotacion, on_delete=models.PROTECT, related_name="votaciones")
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    descripcion = models.TextField()
    fecha_apertura = models.DateTimeField()
    fecha_cierre = models.DateTimeField()
    estado = models.CharField(max_length=15, choices=Estado.choices, default=Estado.BORRADOR)
    publicada = models.BooleanField(default=False)
    resultados_publicos = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "votación"
        verbose_name_plural = "votaciones"
        ordering = ["-fecha_apertura", "nombre"]

    def clean(self):
        errors = {}
        if self.fecha_cierre and self.fecha_apertura and self.fecha_cierre <= self.fecha_apertura:
            errors["fecha_cierre"] = "El cierre debe ser posterior a la apertura."
        if self.publicada and (self.categoria.estado != EstadoBase.ACTIVO or not self.categoria.visible_publicamente):
            errors["publicada"] = "La categoría debe estar activa y visible antes de publicar la votación."
        if errors:
            raise ValidationError(errors)

    def get_absolute_url(self):
        return reverse("elecciones:detalle", kwargs={"slug": self.slug})

    def __str__(self):
        return self.nombre


class Opcion(models.Model):
    votacion = models.ForeignKey(Votacion, on_delete=models.PROTECT, related_name="opciones")
    nombre = models.CharField(max_length=180)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to="opciones/", blank=True)
    orden = models.PositiveIntegerField(default=1)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "opción"
        verbose_name_plural = "opciones"
        ordering = ["orden", "nombre"]
        constraints = [models.UniqueConstraint(fields=["votacion", "nombre"], name="opcion_nombre_unico_por_votacion")]

    def __str__(self):
        return self.nombre
