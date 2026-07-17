from django.urls import path

from . import views

app_name = "cotizaciones"

urlpatterns = [

    # Cotizaciones
    path(
        "",
        views.cotizacion_lista,
        name="cotizacion_lista",
    ),

    path(
        "nueva/",
        views.cotizacion_crear,
        name="cotizacion_crear",
    ),

    path(
        "<int:pk>/",
        views.cotizacion_detalle,
        name="cotizacion_detalle",
    ),

    path(
        "<int:pk>/editar/",
        views.cotizacion_editar,
        name="cotizacion_editar",
    ),

    # Ítems
    path(
        "<int:cotizacion_pk>/items/nuevo/",
        views.item_crear,
        name="item_crear",
    ),

    path(
        "items/<int:pk>/editar/",
        views.item_editar,
        name="item_editar",
    ),

    path(
        "items/<int:pk>/eliminar/",
        views.item_eliminar,
        name="item_eliminar",
    ),
]