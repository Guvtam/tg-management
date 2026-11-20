from django.urls import path

from . import views


app_name = "finanzas"


urlpatterns = [
    path("cobros/", views.bandeja_cobros, name="bandeja_cobros"),
    path("cobros/enlace/<str:token>/", views.detalle_cobro_publico, name="detalle_cobro_publico"),
    path("cobros/cotizacion/<int:cotizacion_pk>/previsualizar/", views.vista_previa_cobros, name="vista_previa_cobros"),
    path("cobros/cotizacion/<int:cotizacion_pk>/confirmar/", views.confirmar_cobros_cotizacion, name="confirmar_cobros_cotizacion"),
    path(
        "",
        views.finanzas_inicio,
        name="finanzas_inicio",
    ),
    path(
        "ingresos/nuevo/",
        views.ingreso_crear,
        name="ingreso_crear",
    ),
    path(
        "ingresos/<int:pk>/editar/",
        views.ingreso_editar,
        name="ingreso_editar",
    ),
    path(
        "ingresos/<int:pk>/eliminar/",
        views.ingreso_eliminar,
        name="ingreso_eliminar",
    ),
    path(
        "gastos/nuevo/",
        views.gasto_crear,
        name="gasto_crear",
    ),
    path(
        "gastos/<int:pk>/editar/",
        views.gasto_editar,
        name="gasto_editar",
    ),
    path(
        "gastos/<int:pk>/eliminar/",
        views.gasto_eliminar,
        name="gasto_eliminar",
    ),
    path(
        "ajax/proyectos/",
        views.obtener_proyectos,
        name="ajax_proyectos",
    ),

    path(
        "ajax/cotizaciones/",
        views.obtener_cotizaciones,
        name="ajax_cotizaciones",
    ),
]