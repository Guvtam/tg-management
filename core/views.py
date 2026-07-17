from django.shortcuts import render

from crm.models import Actividad, Contacto, Empresa, Oportunidad


def dashboard(request):
    contexto = {
        "total_empresas": Empresa.objects.count(),
        "total_contactos": Contacto.objects.count(),
        "total_oportunidades": Oportunidad.objects.count(),
        "oportunidades_ganadas": Oportunidad.objects.filter(
            etapa=Oportunidad.Etapa.GANADA
        ).count(),
        "actividades_pendientes": Actividad.objects.filter(
            estado=Actividad.EstadoActividad.PENDIENTE
        ).count(),
        "ultimas_oportunidades": Oportunidad.objects.select_related(
            "empresa",
            "responsable",
        )[:5],
    }

    return render(request, "core/dashboard.html", contexto)