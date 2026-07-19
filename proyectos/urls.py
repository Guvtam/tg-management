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

    # Actividades
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

    # Documentos
    path(
        "<int:proyecto_pk>/documentos/nuevo/",
        views.documento_crear,
        name="documento_crear",
    ),
    path(
        "documentos/<int:pk>/editar/",
        views.documento_editar,
        name="documento_editar",
    ),
    path(
        "documentos/<int:pk>/visualizar/",
        views.documento_visualizar,
        name="documento_visualizar",
    ),
    path(
        "documentos/<int:pk>/descargar/",
        views.documento_descargar,
        name="documento_descargar",
    ),
    path(
        "documentos/<int:pk>/eliminar/",
        views.documento_eliminar,
        name="documento_eliminar",
    ),

    # Proyecto
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