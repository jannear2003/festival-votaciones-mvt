from django.contrib import admin
from .models import Categoria, Edicion, Festival, Opcion, TipoVotacion, Votacion


class CategoriaInline(admin.TabularInline):
    model = Categoria
    extra = 0
    fields = ("nombre", "orden", "estado", "visible_publicamente")


class OpcionInline(admin.TabularInline):
    model = Opcion
    extra = 1
    fields = ("nombre", "orden", "activa")


@admin.register(Festival)
class FestivalAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo", "creado_en")
    list_filter = ("activo",)
    search_fields = ("nombre",)


@admin.register(Edicion)
class EdicionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "festival", "anio", "estado", "fecha_inicio", "fecha_fin")
    list_filter = ("estado", "festival", "anio")
    search_fields = ("nombre", "festival__nombre")
    inlines = [CategoriaInline]


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "edicion", "orden", "estado", "visible_publicamente", "actualizado_en")
    list_filter = ("estado", "visible_publicamente", "edicion__festival", "edicion")
    search_fields = ("nombre", "edicion__nombre")
    list_editable = ("orden", "estado", "visible_publicamente")
    autocomplete_fields = ("edicion",)


@admin.register(TipoVotacion)
class TipoVotacionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre",)


@admin.register(Votacion)
class VotacionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "tipo", "estado", "publicada", "fecha_apertura", "fecha_cierre")
    list_filter = ("estado", "publicada", "tipo", "categoria__edicion")
    search_fields = ("nombre", "categoria__nombre", "categoria__edicion__nombre")
    prepopulated_fields = {"slug": ("nombre",)}
    autocomplete_fields = ("categoria", "tipo")
    inlines = [OpcionInline]


@admin.register(Opcion)
class OpcionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "votacion", "orden", "activa")
    list_filter = ("activa", "votacion__categoria__edicion")
    search_fields = ("nombre", "votacion__nombre")
    autocomplete_fields = ("votacion",)

admin.site.site_header = "Administración Festival Vallenato"
admin.site.site_title = "Festival Vallenato"
admin.site.index_title = "Configuración de ediciones y votaciones"

from .models import Participacion, Voto

@admin.register(Participacion)
class ParticipacionAdmin(admin.ModelAdmin):
    list_display = ("referencia", "votacion", "estado", "iniciada_en", "confirmada_en")
    list_filter = ("estado", "votacion")
    search_fields = ("referencia", "votacion__nombre")
    readonly_fields = ("referencia", "clave_sesion", "iniciada_en", "confirmada_en")

@admin.register(Voto)
class VotoAdmin(admin.ModelAdmin):
    list_display = ("participacion", "votacion", "opcion", "registrado_en")
    list_filter = ("votacion", "registrado_en")
    search_fields = ("participacion__referencia", "votacion__nombre")
    readonly_fields = ("participacion", "votacion", "opcion", "registrado_en")

from .models import EventoAuditoria, PublicacionResultado

@admin.register(PublicacionResultado)
class PublicacionResultadoAdmin(admin.ModelAdmin):
    list_display = ("votacion", "version", "activa", "publicada_por", "publicada_en", "retirada_en")
    list_filter = ("activa", "votacion")
    search_fields = ("votacion__nombre", "observacion")
    readonly_fields = ("votacion", "version", "resumen", "observacion", "publicada_por", "publicada_en", "activa", "retirada_en")

@admin.register(EventoAuditoria)
class EventoAuditoriaAdmin(admin.ModelAdmin):
    list_display = ("creado_en", "usuario", "accion", "entidad", "identificador", "direccion_ip")
    list_filter = ("accion", "entidad", "creado_en")
    search_fields = ("accion", "entidad", "identificador", "usuario__username")
    readonly_fields = ("usuario", "accion", "entidad", "identificador", "detalle", "direccion_ip", "creado_en")
