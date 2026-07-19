from django.contrib import admin

from .models import Gasto, Ingreso


@admin.register(Ingreso)
class IngresoAdmin(admin.ModelAdmin):
    list_display = [
        "concepto",
        "empresa",
        "monto",
        "moneda",
        "fecha_emision",
        "fecha_vencimiento",
        "estado",
    ]

    list_filter = [
        "estado",
        "moneda",
        "fecha_emision",
    ]

    search_fields = [
        "concepto",
        "empresa__nombre",
        "proyecto__nombre",
        "cotizacion__numero",
    ]


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = [
        "concepto",
        "categoria",
        "proveedor",
        "monto",
        "moneda",
        "fecha",
        "proyecto",
    ]

    list_filter = [
        "categoria",
        "moneda",
        "fecha",
    ]

    search_fields = [
        "concepto",
        "proveedor",
        "proyecto__nombre",
    ]