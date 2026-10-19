from django.contrib import admin

from .models import Participante


@admin.register(Participante)
class ParticipanteAdmin(admin.ModelAdmin):
    list_display = (
        "nombre_artistico",
        "tipo",
        "responsable",
        "ciudad",
        "departamento",
        "pais",
        "activo",
        "creado_en",
    )
    list_filter = (
        "tipo",
        "activo",
        "pais",
        "departamento",
        "creado_en",
    )
    search_fields = (
        "nombre_artistico",
        "nombre_legal",
        "responsable__username",
        "responsable__email",
        "correo_contacto",
        "ciudad",
        "departamento",
    )
    autocomplete_fields = (
        "responsable",
    )
    readonly_fields = (
        "creado_en",
        "actualizado_en",
    )
    ordering = (
        "nombre_artistico",
    )
    list_per_page = 25
    date_hierarchy = "creado_en"
    save_on_top = True

    fieldsets = (
        (
            "Identificación del participante",
            {
                "fields": (
                    "responsable",
                    "tipo",
                    "nombre_artistico",
                    "nombre_legal",
                    "activo",
                )
            },
        ),
        (
            "Procedencia",
            {
                "fields": (
                    "ciudad",
                    "departamento",
                    "pais",
                )
            },
        ),
        (
            "Información de contacto",
            {
                "fields": (
                    "correo_contacto",
                    "telefono_contacto",
                )
            },
        ),
        (
            "Perfil artístico",
            {
                "fields": (
                    "biografia",
                    "fotografia",
                )
            },
        ),
        (
            "Auditoría",
            {
                "fields": (
                    "creado_en",
                    "actualizado_en",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )
