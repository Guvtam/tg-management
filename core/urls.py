from django.urls import path

from . import views


app_name = "core"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("solicitudes-web/", views.solicitudes_web, name="solicitudes_web"),
    path("solicitudes-web/<int:pk>/", views.solicitud_web_detalle, name="solicitud_web_detalle"),
    path("solicitudes-web/<int:pk>/convertir/", views.convertir_solicitud_web, name="convertir_solicitud_web"),
]