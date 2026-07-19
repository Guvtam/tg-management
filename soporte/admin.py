from django.contrib import admin

from .models import InteraccionTicket, Ticket


class InteraccionTicketInline(admin.TabularInline):
    model = InteraccionTicket
    extra = 0
    readonly_fields = ["fecha_creacion"]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [
        "codigo",
        "titulo",
        "empresa",
        "prioridad",
        "estado",
        "responsable",
        "fecha_reporte",
        "fecha_limite_respuesta",
    ]
    list_filter = ["estado", "prioridad", "categoria", "canal"]
    search_fields = ["codigo", "titulo", "empresa__razon_social", "empresa__nombre_fantasia"]
    readonly_fields = ["codigo", "fecha_limite_respuesta"]
    inlines = [InteraccionTicketInline]


@admin.register(InteraccionTicket)
class InteraccionTicketAdmin(admin.ModelAdmin):
    list_display = ["ticket", "tipo", "autor", "fecha_creacion"]
    list_filter = ["tipo"]
