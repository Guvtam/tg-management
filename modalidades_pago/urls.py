from django.urls import path

from . import views

app_name = "modalidades_pago"

urlpatterns = [
    path("", views.modalidad_lista, name="lista"),
    path("cotizacion/<int:cotizacion_pk>/", views.modalidad_detalle, name="detalle"),
    path("cotizacion/<int:cotizacion_pk>/configurar/", views.modalidad_configurar, name="configurar"),
    path("cotizacion/<int:cotizacion_pk>/eliminar/", views.modalidad_eliminar, name="eliminar"),
]
