from django.urls import path

from . import views

app_name = "encuestas"

urlpatterns = [
    path("", views.encuesta_lista, name="lista"),
    path("nueva/", views.encuesta_crear, name="crear"),
    path(
        "proyecto/<int:proyecto_pk>/nueva/",
        views.encuesta_crear,
        name="crear_desde_proyecto",
    ),
    path("<int:pk>/", views.encuesta_detalle, name="detalle"),
    path(
        "<int:pk>/marcar-enviada/",
        views.encuesta_marcar_enviada,
        name="marcar_enviada",
    ),
    path("<int:pk>/anular/", views.encuesta_anular, name="anular"),
    path("responder/<uuid:token>/", views.encuesta_responder, name="responder"),
    path("gracias/<uuid:token>/", views.encuesta_gracias, name="gracias"),
]
