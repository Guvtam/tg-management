from django.urls import path

from . import views


app_name = "proyectos"


urlpatterns = [
    path(
        "",
        views.proyecto_lista,
        name="proyecto_lista",
    ),
    path(
        "nuevo/",
        views.proyecto_crear,
        name="proyecto_crear",
    ),
    path(
        "cotizaciones-por-empresa/",
        views.cotizaciones_por_empresa,
        name="cotizaciones_por_empresa",
    ),

    path(
        "<int:proyecto_pk>/actividades/nueva/",
        views.actividad_crear,
        name="actividad_crear",
    ),
    path(
        "actividades/<int:pk>/editar/",
        views.actividad_editar,
        name="actividad_editar",
    ),
    path(
        "actividades/<int:pk>/eliminar/",
        views.actividad_eliminar,
        name="actividad_eliminar",
    ),

    path(
        "<int:pk>/editar/",
        views.proyecto_editar,
        name="proyecto_editar",
    ),
    path(
        "<int:pk>/",
        views.proyecto_detalle,
        name="proyecto_detalle",
    ),
]