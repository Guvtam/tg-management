from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from proyectos.models import Proyecto

from .forms import EncuestaCrearForm, EncuestaRespuestaForm
from .models import EncuestaSatisfaccion


@login_required
def encuesta_lista(request):
    encuestas = EncuestaSatisfaccion.objects.select_related(
        "proyecto", "empresa", "contacto"
    )
    estado = request.GET.get("estado", "").strip()
    buscar = request.GET.get("q", "").strip()

    if estado:
        encuestas = encuestas.filter(estado=estado)
    if buscar:
        encuestas = encuestas.filter(
            Q(proyecto__codigo__icontains=buscar)
            | Q(proyecto__nombre__icontains=buscar)
            | Q(empresa__razon_social__icontains=buscar)
            | Q(empresa__nombre_fantasia__icontains=buscar)
        )

    respondidas = EncuestaSatisfaccion.objects.filter(
        estado=EncuestaSatisfaccion.Estado.RESPONDIDA
    )
    resumen = respondidas.aggregate(
        total=Count("id"),
        satisfaccion=Avg("satisfaccion_general"),
        calidad=Avg("calidad_solucion"),
    )
    total_encuestas = EncuestaSatisfaccion.objects.count()
    total_respondidas = resumen["total"] or 0
    tasa_respuesta = (
        round(total_respondidas * 100 / total_encuestas)
        if total_encuestas
        else 0
    )
    promotores = respondidas.filter(recomendacion__gte=9).count()
    detractores = respondidas.filter(recomendacion__lte=6).count()
    nps = (
        round((promotores - detractores) * 100 / total_respondidas)
        if total_respondidas
        else 0
    )

    return render(
        request,
        "encuestas/encuesta_lista.html",
        {
            "encuestas": encuestas,
            "estados": EncuestaSatisfaccion.Estado.choices,
            "estado_actual": estado,
            "buscar": buscar,
            "total_encuestas": total_encuestas,
            "total_respondidas": total_respondidas,
            "tasa_respuesta": tasa_respuesta,
            "promedio_satisfaccion": resumen["satisfaccion"],
            "nps": nps,
        },
    )


@login_required
def encuesta_crear(request, proyecto_pk=None):
    proyecto = None
    if proyecto_pk is not None:
        proyecto = get_object_or_404(Proyecto, pk=proyecto_pk)
        existente = EncuestaSatisfaccion.objects.filter(proyecto=proyecto).first()
        if existente:
            messages.info(request, "Este proyecto ya tiene una encuesta asociada.")
            return redirect("encuestas:detalle", pk=existente.pk)

    if request.method == "POST":
        form = EncuestaCrearForm(request.POST, proyecto=proyecto)
        if form.is_valid():
            encuesta = form.save(commit=False)
            encuesta.empresa = encuesta.proyecto.empresa
            encuesta.creado_por = request.user
            encuesta.save()
            messages.success(request, "Encuesta creada correctamente.")
            return redirect("encuestas:detalle", pk=encuesta.pk)
    else:
        form = EncuestaCrearForm(proyecto=proyecto)

    return render(
        request,
        "encuestas/encuesta_form.html",
        {"form": form, "proyecto": proyecto},
    )


@login_required
def encuesta_detalle(request, pk):
    encuesta = get_object_or_404(
        EncuestaSatisfaccion.objects.select_related(
            "proyecto", "empresa", "contacto", "creado_por"
        ),
        pk=pk,
    )
    url_publica = request.build_absolute_uri(encuesta.get_url_publica())
    return render(
        request,
        "encuestas/encuesta_detalle.html",
        {"encuesta": encuesta, "url_publica": url_publica},
    )


@login_required
@require_POST
def encuesta_marcar_enviada(request, pk):
    encuesta = get_object_or_404(EncuestaSatisfaccion, pk=pk)
    if encuesta.respondida:
        messages.warning(request, "La encuesta ya fue respondida.")
    else:
        encuesta.estado = EncuestaSatisfaccion.Estado.ENVIADA
        encuesta.fecha_envio = timezone.now()
        encuesta.save(update_fields=["estado", "fecha_envio", "actualizado_en"])
        messages.success(request, "Encuesta marcada como enviada.")
    return redirect("encuestas:detalle", pk=encuesta.pk)


@login_required
@require_POST
def encuesta_anular(request, pk):
    encuesta = get_object_or_404(EncuestaSatisfaccion, pk=pk)
    if encuesta.respondida:
        messages.warning(request, "No se puede anular una encuesta respondida.")
    else:
        encuesta.estado = EncuestaSatisfaccion.Estado.ANULADA
        encuesta.save(update_fields=["estado", "actualizado_en"])
        messages.success(request, "Encuesta anulada.")
    return redirect("encuestas:detalle", pk=encuesta.pk)


def encuesta_responder(request, token):
    encuesta = get_object_or_404(
        EncuestaSatisfaccion.objects.select_related("proyecto", "empresa"),
        token=token,
    )

    if encuesta.estado == EncuestaSatisfaccion.Estado.ANULADA:
        return render(request, "encuestas/encuesta_no_disponible.html", status=410)
    if encuesta.fecha_vencimiento and encuesta.fecha_vencimiento < timezone.localdate():
        if encuesta.estado != EncuestaSatisfaccion.Estado.RESPONDIDA:
            EncuestaSatisfaccion.objects.filter(pk=encuesta.pk).update(
                estado=EncuestaSatisfaccion.Estado.VENCIDA
            )
        return render(request, "encuestas/encuesta_no_disponible.html", status=410)
    if encuesta.respondida:
        return render(request, "encuestas/encuesta_ya_respondida.html")

    if request.method == "POST":
        form = EncuestaRespuestaForm(request.POST, instance=encuesta)
        if form.is_valid():
            encuesta = form.save(commit=False)
            encuesta.estado = EncuestaSatisfaccion.Estado.RESPONDIDA
            encuesta.fecha_respuesta = timezone.now()
            encuesta.save()
            return redirect("encuestas:gracias", token=encuesta.token)
    elif request.method == "GET":
        form = EncuestaRespuestaForm(instance=encuesta)
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

    return render(
        request,
        "encuestas/encuesta_responder.html",
        {"encuesta": encuesta, "form": form},
    )


def encuesta_gracias(request, token):
    encuesta = get_object_or_404(EncuestaSatisfaccion, token=token)
    if not encuesta.respondida:
        return redirect("encuestas:responder", token=token)
    return render(request, "encuestas/encuesta_gracias.html", {"encuesta": encuesta})
