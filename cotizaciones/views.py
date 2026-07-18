from django.contrib import messages
from django.db.models import Max, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template
from django.utils import timezone
from xhtml2pdf import pisa

from .forms import CotizacionForm, ItemCotizacionForm
from .models import Cotizacion, ItemCotizacion


def cotizacion_lista(request):
    """
    Muestra todas las cotizaciones y permite filtrar por:
    - Texto de búsqueda
    - Estado
    - Moneda
    """

    busqueda = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "").strip()
    moneda = request.GET.get("moneda", "").strip()

    cotizaciones = Cotizacion.objects.select_related(
        "oportunidad",
        "oportunidad__empresa",
        "contacto",
        "creado_por",
    ).all()

    if busqueda:
        cotizaciones = cotizaciones.filter(
            Q(numero__icontains=busqueda)
            | Q(oportunidad__titulo__icontains=busqueda)
            | Q(
                oportunidad__empresa__razon_social__icontains=busqueda
            )
            | Q(
                oportunidad__empresa__nombre_fantasia__icontains=busqueda
            )
        )

    if estado:
        cotizaciones = cotizaciones.filter(
            estado=estado,
        )

    if moneda:
        cotizaciones = cotizaciones.filter(
            moneda=moneda,
        )

    contexto = {
        "cotizaciones": cotizaciones,
        "busqueda": busqueda,
        "estado_seleccionado": estado,
        "moneda_seleccionada": moneda,
        "estados": Cotizacion.Estado.choices,
        "monedas": Cotizacion.Moneda.choices,
    }

    return render(
        request,
        "cotizaciones/cotizacion_lista.html",
        contexto,
    )


def cotizacion_crear(request):
    """
    Crea una nueva cotización.

    Puede recibir una oportunidad mediante:
    /cotizaciones/nueva/?oportunidad=3
    """

    oportunidad_id = request.GET.get("oportunidad")

    if request.method == "POST":
        form = CotizacionForm(
            request.POST,
        )

        if form.is_valid():
            cotizacion = form.save(
                commit=False
            )

            if request.user.is_authenticated:
                cotizacion.creado_por = request.user

            cotizacion.save()

            messages.success(
                request,
                (
                    f"La cotización {cotizacion.numero} "
                    "fue creada correctamente."
                ),
            )

            return redirect(
                "cotizaciones:cotizacion_detalle",
                pk=cotizacion.pk,
            )

    else:
        datos_iniciales = {
            "fecha_emision": timezone.localdate(),
            "estado": Cotizacion.Estado.BORRADOR,
            "moneda": Cotizacion.Moneda.CLP,
            "valor_moneda": 1,
            "descuento_porcentaje": 0,
            "impuesto_porcentaje": 19,
            "validez_oferta": "15 días",
        }

        if oportunidad_id:
            datos_iniciales["oportunidad"] = oportunidad_id

        form = CotizacionForm(
            initial=datos_iniciales,
        )

    contexto = {
        "form": form,
        "titulo": "Nueva cotización",
        "texto_boton": "Guardar cotización",
    }

    return render(
        request,
        "cotizaciones/cotizacion_formulario.html",
        contexto,
    )


def cotizacion_detalle(request, pk):
    """
    Muestra la cabecera, los ítems y los totales
    calculados de una cotización.
    """

    cotizacion = get_object_or_404(
        Cotizacion.objects.select_related(
            "oportunidad",
            "oportunidad__empresa",
            "contacto",
            "creado_por",
        ).prefetch_related(
            "items",
        ),
        pk=pk,
    )

    contexto = {
        "cotizacion": cotizacion,
    }

    return render(
        request,
        "cotizaciones/cotizacion_detalle.html",
        contexto,
    )

def cotizacion_exportar_pdf(request, pk):
    """
    Genera y descarga una cotización en formato PDF.
    """

    cotizacion = get_object_or_404(
        Cotizacion.objects.select_related(
            "oportunidad",
            "oportunidad__empresa",
            "contacto",
            "creado_por",
        ).prefetch_related(
            "items",
        ),
        pk=pk,
    )

    template = get_template(
        "cotizaciones/cotizacion_pdf.html"
    )

    contexto = {
        "cotizacion": cotizacion,
    }

    html = template.render(
        contexto
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    nombre_archivo = (
        f"{cotizacion.numero}.pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{nombre_archivo}"'
    )

    resultado = pisa.CreatePDF(
        html,
        dest=response,
        encoding="UTF-8",
    )

    if resultado.err:
        return HttpResponse(
            "Ocurrió un error al generar el PDF.",
            status=500,
        )

    return response




def cotizacion_editar(request, pk):
    """
    Permite editar la cabecera y condiciones
    comerciales de una cotización.
    """

    cotizacion = get_object_or_404(
        Cotizacion,
        pk=pk,
    )

    if request.method == "POST":
        form = CotizacionForm(
            request.POST,
            instance=cotizacion,
        )

        if form.is_valid():
            cotizacion = form.save()

            messages.success(
                request,
                (
                    f"La cotización {cotizacion.numero} "
                    "fue actualizada correctamente."
                ),
            )

            return redirect(
                "cotizaciones:cotizacion_detalle",
                pk=cotizacion.pk,
            )

    else:
        form = CotizacionForm(
            instance=cotizacion,
        )

    contexto = {
        "form": form,
        "cotizacion": cotizacion,
        "titulo": f"Editar cotización {cotizacion.numero}",
        "texto_boton": "Guardar cambios",
    }

    return render(
        request,
        "cotizaciones/cotizacion_formulario.html",
        contexto,
    )


def item_crear(request, cotizacion_pk):
    """
    Agrega un nuevo ítem a una cotización.
    """

    cotizacion = get_object_or_404(
        Cotizacion.objects.select_related(
            "oportunidad",
            "oportunidad__empresa",
        ),
        pk=cotizacion_pk,
    )

    ultimo_orden = cotizacion.items.aggregate(
        ultimo=Max("orden")
    )["ultimo"]

    siguiente_orden = (
        ultimo_orden + 1
        if ultimo_orden is not None
        else 1
    )

    if request.method == "POST":
        form = ItemCotizacionForm(
            request.POST,
        )

        if form.is_valid():
            item = form.save(
                commit=False
            )

            item.cotizacion = cotizacion
            item.save()

            messages.success(
                request,
                (
                    f'El ítem "{item.descripcion}" '
                    "fue agregado correctamente."
                ),
            )

            return redirect(
                "cotizaciones:cotizacion_detalle",
                pk=cotizacion.pk,
            )

    else:
        form = ItemCotizacionForm(
            initial={
                "orden": siguiente_orden,
                "cantidad": 1,
                "unidad": "Unidad",
                "descuento_porcentaje": 0,
            }
        )

    contexto = {
        "form": form,
        "cotizacion": cotizacion,
        "titulo": "Agregar ítem",
        "texto_boton": "Agregar ítem",
    }

    return render(
        request,
        "cotizaciones/item_formulario.html",
        contexto,
    )


def item_editar(request, pk):
    """
    Permite editar un ítem existente.
    """

    item = get_object_or_404(
        ItemCotizacion.objects.select_related(
            "cotizacion",
            "cotizacion__oportunidad",
            "cotizacion__oportunidad__empresa",
        ),
        pk=pk,
    )

    cotizacion = item.cotizacion

    if request.method == "POST":
        form = ItemCotizacionForm(
            request.POST,
            instance=item,
        )

        if form.is_valid():
            codigo_original = item.codigo

            item = form.save(
                commit=False
            )

            item.codigo = codigo_original
            item.save()

            messages.success(
                request,
                (
                    f'El ítem "{item.descripcion}" '
                    "fue actualizado correctamente."
                ),
            )

            return redirect(
                "cotizaciones:cotizacion_detalle",
                pk=cotizacion.pk,
            )

    else:
        form = ItemCotizacionForm(
            instance=item,
        )

    contexto = {
        "form": form,
        "cotizacion": cotizacion,
        "item": item,
        "titulo": "Editar ítem",
        "texto_boton": "Guardar cambios",
    }

    return render(
        request,
        "cotizaciones/item_formulario.html",
        contexto,
    )


def item_eliminar(request, pk):
    """
    Solicita confirmación y elimina un ítem.
    """

    item = get_object_or_404(
        ItemCotizacion.objects.select_related(
            "cotizacion",
        ),
        pk=pk,
    )

    cotizacion = item.cotizacion

    if request.method == "POST":
        descripcion = item.descripcion

        item.delete()

        messages.success(
            request,
            (
                f'El ítem "{descripcion}" '
                "fue eliminado correctamente."
            ),
        )

        return redirect(
            "cotizaciones:cotizacion_detalle",
            pk=cotizacion.pk,
        )

    contexto = {
        "item": item,
    }

    return render(
        request,
        "cotizaciones/item_confirmar_eliminar.html",
        contexto,
    )

def cotizacion_ver_pdf(request, pk):
    """
    Genera la cotización en PDF y la muestra
    directamente en el navegador.
    """

    cotizacion = get_object_or_404(
        Cotizacion.objects.select_related(
            "oportunidad",
            "oportunidad__empresa",
            "contacto",
            "creado_por",
        ).prefetch_related(
            "items",
        ),
        pk=pk,
    )

    template = get_template(
        "cotizaciones/cotizacion_pdf.html"
    )

    contexto = {
        "cotizacion": cotizacion,
    }

    html = template.render(contexto)

    response = HttpResponse(
        content_type="application/pdf"
    )

    nombre_archivo = f"{cotizacion.numero}.pdf"

    response["Content-Disposition"] = (
        f'inline; filename="{nombre_archivo}"'
    )

    resultado = pisa.CreatePDF(
        html,
        dest=response,
        encoding="UTF-8",
    )

    if resultado.err:
        return HttpResponse(
            "Ocurrió un error al generar el PDF.",
            status=500,
        )

    return response