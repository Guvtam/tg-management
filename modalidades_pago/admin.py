from django.contrib import admin

from .models import ModalidadPagoCotizacion


@admin.register(ModalidadPagoCotizacion)
class ModalidadPagoCotizacionAdmin(admin.ModelAdmin):
    list_display = (
        "cotizacion",
        "mostrar_pago_unico",
        "mostrar_plan_12_meses",
        "porcentaje_pie",
        "mantencion_mensual",
        "fecha_actualizacion",
    )
    search_fields = (
        "cotizacion__numero",
        "cotizacion__oportunidad__titulo",
        "cotizacion__oportunidad__empresa__razon_social",
    )
    list_filter = ("mostrar_pago_unico", "mostrar_plan_12_meses")
