from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from cotizaciones.models import Cotizacion

from .forms import ModalidadPagoCotizacionForm
from .models import ModalidadPagoCotizacion


def modalidad_lista(request):
    busqueda = request.GET.get("q", "").strip()
    cotizaciones = (
        Cotizacion.objects
        .select_related("oportunidad", "oportunidad__empresa")
        .select_related("configuracion_modalidades_pago")
    )
    if busqueda:
        cotizaciones = cotizaciones.filter(
            Q(numero__icontains=busqueda)
            | Q(oportunidad__titulo__icontains=busqueda)
            | Q(oportunidad__empresa__razon_social__icontains=busqueda)
            | Q(oportunidad__empresa__nombre_fantasia__icontains=busqueda)
        )
    return render(
        request,
        "modalidades_pago/modalidad_lista.html",
        {"cotizaciones": cotizaciones, "busqueda": busqueda},
    )


def modalidad_configurar(request, cotizacion_pk):
    cotizacion = get_object_or_404(
        Cotizacion.objects.select_related("oportunidad", "oportunidad__empresa"),
        pk=cotizacion_pk,
    )
    instancia = ModalidadPagoCotizacion.objects.filter(cotizacion=cotizacion).first()
    if request.method == "POST":
        form = ModalidadPagoCotizacionForm(request.POST, instance=instancia)
        if form.is_valid():
            modalidad = form.save(commit=False)
            modalidad.cotizacion = cotizacion
            modalidad.save()
            messages.success(request, "Modalidades de pago guardadas correctamente.")
            return redirect("modalidades_pago:detalle", cotizacion_pk=cotizacion.pk)
    else:
        form = ModalidadPagoCotizacionForm(instance=instancia)
    return render(
        request,
        "modalidades_pago/modalidad_formulario.html",
        {"form": form, "cotizacion": cotizacion, "modalidad": instancia},
    )


def modalidad_detalle(request, cotizacion_pk):
    cotizacion = get_object_or_404(
        Cotizacion.objects.select_related("oportunidad", "oportunidad__empresa"),
        pk=cotizacion_pk,
    )
    modalidad = get_object_or_404(ModalidadPagoCotizacion, cotizacion=cotizacion)
    return render(
        request,
        "modalidades_pago/modalidad_detalle.html",
        {"cotizacion": cotizacion, "modalidad": modalidad},
    )


def modalidad_eliminar(request, cotizacion_pk):
    cotizacion = get_object_or_404(Cotizacion, pk=cotizacion_pk)
    modalidad = get_object_or_404(ModalidadPagoCotizacion, cotizacion=cotizacion)
    if request.method == "POST":
        modalidad.delete()
        messages.success(request, "Configuración de modalidades eliminada.")
        return redirect("modalidades_pago:lista")
    return render(
        request,
        "modalidades_pago/modalidad_confirmar_eliminar.html",
        {"cotizacion": cotizacion, "modalidad": modalidad},
    )
