from django.contrib import admin

from .models import EncuestaSatisfaccion


@admin.register(EncuestaSatisfaccion)
class EncuestaSatisfaccionAdmin(admin.ModelAdmin):
    list_display = (
        "proyecto",
        "empresa",
        "estado",
        "satisfaccion_general",
        "recomendacion",
        "fecha_respuesta",
    )
    list_filter = ("estado", "autoriza_testimonio", "creado_en")
    search_fields = (
        "proyecto__codigo",
        "proyecto__nombre",
        "empresa__razon_social",
        "empresa__nombre_fantasia",
    )
    readonly_fields = (
        "token",
        "fecha_envio",
        "fecha_respuesta",
        "creado_en",
        "actualizado_en",
    )
