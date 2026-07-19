from django.contrib import admin

from .models import ActividadProyecto, DocumentoProyecto, Proyecto


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

    readonly_fields = (
        "codigo",
        "creado_en",
        "actualizado_en",
    )


@admin.register(ActividadProyecto)
class ActividadProyectoAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "proyecto",
        "tipo",
        "responsable",
        "estado",
        "fecha",
    )

    list_filter = (
        "tipo",
        "estado",
        "responsable",
    )

    search_fields = (
        "titulo",
        "proyecto__codigo",
        "proyecto__nombre",
    )


@admin.register(DocumentoProyecto)
class DocumentoProyectoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "proyecto",
        "tipo",
        "nombre_archivo",
        "cargado_por",
        "creado_en",
    )

    list_filter = (
        "tipo",
        "creado_en",
    )

    search_fields = (
        "nombre",
        "descripcion",
        "proyecto__codigo",
        "proyecto__nombre",
        "proyecto__empresa__nombre",
    )

    readonly_fields = (
        "creado_en",
        "actualizado_en",
    )

    list_select_related = (
        "proyecto",
        "proyecto__empresa",
        "cargado_por",
    )