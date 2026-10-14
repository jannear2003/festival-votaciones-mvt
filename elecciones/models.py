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

class Participacion(models.Model):
    class Estado(models.TextChoices):
        INICIADA = "INICIADA", "Iniciada"
        CONFIRMADA = "CONFIRMADA", "Confirmada"
        ANULADA = "ANULADA", "Anulada"

    votacion = models.ForeignKey(Votacion, on_delete=models.PROTECT, related_name="participaciones")
    referencia = models.CharField(max_length=40, unique=True)
    clave_sesion = models.CharField(max_length=40)
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.INICIADA)
    iniciada_en = models.DateTimeField(auto_now_add=True)
    confirmada_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "participación"
        verbose_name_plural = "participaciones"
        ordering = ["-iniciada_en"]
        constraints = [models.UniqueConstraint(fields=["votacion", "clave_sesion"], name="una_participacion_por_votacion_y_sesion")]

    def __str__(self):
        return self.referencia


class Voto(models.Model):
    participacion = models.OneToOneField(Participacion, on_delete=models.PROTECT, related_name="voto")
    votacion = models.ForeignKey(Votacion, on_delete=models.PROTECT, related_name="votos")
    opcion = models.ForeignKey(Opcion, on_delete=models.PROTECT, related_name="votos")
    registrado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "voto"
        verbose_name_plural = "votos"
        ordering = ["-registrado_en"]
        constraints = [models.UniqueConstraint(fields=["votacion", "participacion"], name="voto_unico_por_participacion")]

    def clean(self):
        errors = {}
        if self.opcion_id and self.votacion_id and self.opcion.votacion_id != self.votacion_id:
            errors["opcion"] = "La opción seleccionada no pertenece a la votación."
        if self.participacion_id and self.votacion_id and self.participacion.votacion_id != self.votacion_id:
            errors["participacion"] = "La participación no corresponde a la votación."
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.votacion} · {self.participacion.referencia}"

from django.conf import settings


class PublicacionResultado(models.Model):
    votacion = models.ForeignKey(Votacion, on_delete=models.PROTECT, related_name="publicaciones_resultado")
    version = models.PositiveIntegerField()
    resumen = models.JSONField(default=dict)
    observacion = models.TextField(blank=True)
    publicada_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="resultados_publicados")
    publicada_en = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    retirada_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "publicación de resultado"
        verbose_name_plural = "publicaciones de resultados"
        ordering = ["-publicada_en"]
        constraints = [
            models.UniqueConstraint(fields=["votacion", "version"], name="version_resultado_unica_por_votacion")
        ]

    def __str__(self):
        return f"{self.votacion} · versión {self.version}"


class EventoAuditoria(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="eventos_auditoria")
    accion = models.CharField(max_length=80)
    entidad = models.CharField(max_length=80)
    identificador = models.CharField(max_length=80)
    detalle = models.JSONField(default=dict, blank=True)
    direccion_ip = models.GenericIPAddressField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "evento de auditoría"
        verbose_name_plural = "eventos de auditoría"
        ordering = ["-creado_en"]

    def __str__(self):
        return f"{self.accion} · {self.entidad} {self.identificador}"
