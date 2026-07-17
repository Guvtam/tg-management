from django.contrib import admin

from .models import Actividad, Contacto, Empresa, Oportunidad


class ContactoInline(admin.TabularInline):
    model = Contacto
    extra = 0
    fields = (
        "nombres",
        "apellidos",
        "cargo",
        "email",
        "telefono",
        "es_contacto_principal",
        "activo",
    )


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = (
        "razon_social",
        "nombre_fantasia",
        "rut",
        "tipo",
        "comuna",
        "estado",
        "fecha_creacion",
    )
    list_filter = (
        "tipo",
        "estado",
        "region",
    )
    search_fields = (
        "razon_social",
        "nombre_fantasia",
        "rut",
        "email",
        "comuna",
    )
    readonly_fields = (
        "fecha_creacion",
        "fecha_actualizacion",
    )
    inlines = [ContactoInline]

    fieldsets = (
        (
            "Identificación",
            {
                "fields": (
                    "razon_social",
                    "nombre_fantasia",
                    "rut",
                    "tipo",
                    "rubro",
                    "estado",
                )
            },
        ),
        (
            "Información de contacto",
            {
                "fields": (
                    "sitio_web",
                    "telefono",
                    "email",
                    "direccion",
                    "comuna",
                    "region",
                )
            },
        ),
        (
            "Información adicional",
            {
                "fields": (
                    "observaciones",
                    "creado_por",
                )
            },
        ),
        (
            "Control",
            {
                "fields": (
                    "fecha_creacion",
                    "fecha_actualizacion",
                )
            },
        ),
    )


@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = (
        "nombres",
        "apellidos",
        "empresa",
        "cargo",
        "email",
        "telefono",
        "es_contacto_principal",
        "activo",
    )
    list_filter = (
        "activo",
        "es_contacto_principal",
    )
    search_fields = (
        "nombres",
        "apellidos",
        "empresa__razon_social",
        "empresa__nombre_fantasia",
        "email",
    )
    autocomplete_fields = ("empresa",)
    readonly_fields = (
        "fecha_creacion",
        "fecha_actualizacion",
    )


class ActividadInline(admin.TabularInline):
    model = Actividad
    extra = 0
    fields = (
        "tipo",
        "asunto",
        "fecha_programada",
        "estado",
        "responsable",
    )
    show_change_link = True


@admin.register(Oportunidad)
class OportunidadAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "empresa",
        "etapa",
        "prioridad",
        "valor_estimado",
        "probabilidad",
        "fecha_estimada_cierre",
        "responsable",
    )
    list_filter = (
        "etapa",
        "prioridad",
        "responsable",
    )
    search_fields = (
        "titulo",
        "empresa__razon_social",
        "empresa__nombre_fantasia",
        "descripcion",
        "servicio_interes",
    )
    autocomplete_fields = (
        "empresa",
        "contacto",
    )
    readonly_fields = (
        "fecha_creacion",
        "fecha_actualizacion",
    )
    inlines = [ActividadInline]


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = (
        "asunto",
        "oportunidad",
        "tipo",
        "fecha_programada",
        "estado",
        "responsable",
    )
    list_filter = (
        "tipo",
        "estado",
        "responsable",
    )
    search_fields = (
        "asunto",
        "descripcion",
        "oportunidad__titulo",
        "oportunidad__empresa__razon_social",
    )
    autocomplete_fields = (
        "oportunidad",
        "responsable",
    )
    readonly_fields = (
        "fecha_creacion",
        "fecha_actualizacion",
    )