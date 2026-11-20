from django.urls import path

from . import views
from .api import recibir_ticket_web

app_name = "soporte"

urlpatterns = [
    path("api/tickets/", recibir_ticket_web, name="api_tickets"),
    path(
        "tickets/",
        views.ticket_lista,
        name="ticket_lista",
    ),
    path(
        "tickets/nuevo/",
        views.ticket_crear,
        name="ticket_crear",
    ),
    path(
        "tickets/<int:pk>/",
        views.ticket_detalle,
        name="ticket_detalle",
    ),
    path(
        "tickets/<int:pk>/editar/",
        views.ticket_editar,
        name="ticket_editar",
    ),
    path(
        "tickets/<int:pk>/eliminar/",
        views.ticket_eliminar,
        name="ticket_eliminar",
    ),
]
