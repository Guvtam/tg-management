from django.contrib import admin

from .models import Cobro, Gasto, Ingreso


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

@admin.register(Cobro)
class CobroAdmin(admin.ModelAdmin):
    list_display = ["id", "cliente", "concepto", "monto", "vencimiento", "estado", "creado_en"]
    list_filter = ["estado", "creado_en"]
    search_fields = ["ingreso__concepto", "ingreso__empresa__razon_social", "ingreso__cotizacion__numero"]
    list_select_related = ["ingreso", "ingreso__empresa"]
    readonly_fields = ["token", "estado", "proveedor", "referencia_proveedor", "fecha_confirmacion", "creado_en", "actualizado_en"]
    fields = ["ingreso", "token", "estado", "proveedor", "referencia_proveedor", "fecha_confirmacion", "creado_en", "actualizado_en"]

    @admin.display(description="Cliente")
    def cliente(self, obj):
        return obj.ingreso.empresa

    @admin.display(description="Concepto")
    def concepto(self, obj):
        return obj.ingreso.concepto

    @admin.display(description="Monto")
    def monto(self, obj):
        return f"{obj.ingreso.monto} {obj.ingreso.moneda}"

    @admin.display(description="Vencimiento")
    def vencimiento(self, obj):
        return obj.ingreso.fecha_vencimiento

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("ingreso", "ingreso__empresa")

    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)
