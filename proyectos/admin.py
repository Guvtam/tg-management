from django.contrib import admin

from .models import Proyecto


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "nombre",
        "empresa",
        "responsable",
        "estado",
        "prioridad",
        "porcentaje_avance",
        "fecha_alta",
        "fecha_entrega",
    )

    list_filter = (
        "estado",
        "prioridad",
        "responsable",
    )

    search_fields = (
        "codigo",
        "nombre",
        "empresa__nombre",
    )

    ordering = (
        "-creado_en",
    )