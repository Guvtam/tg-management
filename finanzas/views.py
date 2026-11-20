from decimal import Decimal

from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from .models import Cobro
from .plan_cobros import previsualizar_plan
from .confirmar_cobros import confirmar_plan_cobros
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from datetime import date
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from cotizaciones.models import Cotizacion
from proyectos.models import Proyecto

from .forms import GastoForm, IngresoForm
from .models import Gasto, Ingreso, Moneda


def finanzas_inicio(request):
    busqueda = request.GET.get("q", "").strip()
    moneda = request.GET.get(
        "moneda",
        Moneda.CLP,
    )
    fecha_desde = request.GET.get(
        "fecha_desde",
        "",
    )
    fecha_hasta = request.GET.get(
        "fecha_hasta",
        "",
    )
    estado = request.GET.get("estado", "")

    monedas_validas = {
        opcion[0] for opcion in Moneda.choices
    }

    if moneda not in monedas_validas:
        moneda = Moneda.CLP

    ingresos = (
        Ingreso.objects
        .select_related(
            "empresa",
            "proyecto",
            "cotizacion",
        )
        .filter(moneda=moneda)
    )

    gastos = (
        Gasto.objects
        .select_related("proyecto")
        .filter(moneda=moneda)
    )

    if busqueda:
        ingresos = ingresos.filter(
            Q(concepto__icontains=busqueda)
            | Q(empresa__razon_social__icontains=busqueda)
            | Q(empresa__nombre_fantasia__icontains=busqueda)
            | Q(proyecto__nombre__icontains=busqueda)
        )

        gastos = gastos.filter(
            Q(concepto__icontains=busqueda)
            | Q(proveedor__icontains=busqueda)
            | Q(proyecto__nombre__icontains=busqueda)
        )

    if fecha_desde:
        ingresos = ingresos.filter(
            fecha_emision__gte=fecha_desde
        )
        gastos = gastos.filter(
            fecha__gte=fecha_desde
        )

    if fecha_hasta:
        ingresos = ingresos.filter(
            fecha_emision__lte=fecha_hasta
        )
        gastos = gastos.filter(
            fecha__lte=fecha_hasta
        )

    if estado:
        ingresos = ingresos.filter(
            estado=estado
        )

    total_ingresos = (
        ingresos
        .exclude(estado=Ingreso.Estado.ANULADO)
        .aggregate(total=Sum("monto"))
        .get("total")
        or Decimal("0")
    )

    ingresos_pagados = (
        ingresos
        .filter(estado=Ingreso.Estado.PAGADO)
        .aggregate(total=Sum("monto"))
        .get("total")
        or Decimal("0")
    )

    ingresos_pendientes = (
        ingresos
        .filter(
            estado__in=[
                Ingreso.Estado.PENDIENTE,
                Ingreso.Estado.VENCIDO,
            ]
        )
        .aggregate(total=Sum("monto"))
        .get("total")
        or Decimal("0")
    )

    total_gastos = (
        gastos
        .aggregate(total=Sum("monto"))
        .get("total")
        or Decimal("0")
    )

    saldo = ingresos_pagados - total_gastos

    context = {
        "ingresos": ingresos,
        "gastos": gastos,
        "total_ingresos": total_ingresos,
        "ingresos_pagados": ingresos_pagados,
        "ingresos_pendientes": ingresos_pendientes,
        "total_gastos": total_gastos,
        "saldo": saldo,
        "moneda_seleccionada": moneda,
        "monedas": Moneda.choices,
        "estados": Ingreso.Estado.choices,
        "estado_seleccionado": estado,
        "busqueda": busqueda,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
    }

    return render(
        request,
        "finanzas/finanzas_inicio.html",
        context,
    )


def ingreso_crear(request):
    if request.method == "POST":
        form = IngresoForm(request.POST)

        if form.is_valid():
            ingreso = form.save()

            messages.success(
                request,
                "Ingreso registrado correctamente.",
            )

            return redirect(
                "finanzas:finanzas_inicio"
            )
    else:
        form = IngresoForm()

    context = {
        "form": form,
        "titulo": "Nuevo ingreso",
        "boton": "Registrar ingreso",
    }

    return render(
        request,
        "finanzas/ingreso_form.html",
        context,
    )


def ingreso_editar(request, pk):
    ingreso = get_object_or_404(
        Ingreso,
        pk=pk,
    )

    if request.method == "POST":
        form = IngresoForm(
            request.POST,
            instance=ingreso,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Ingreso actualizado correctamente.",
            )

            return redirect(
                "finanzas:finanzas_inicio"
            )
    else:
        form = IngresoForm(
            instance=ingreso,
        )

    context = {
        "form": form,
        "ingreso": ingreso,
        "titulo": "Editar ingreso",
        "boton": "Guardar cambios",
    }

    return render(
        request,
        "finanzas/ingreso_form.html",
        context,
    )


def ingreso_eliminar(request, pk):
    ingreso = get_object_or_404(
        Ingreso,
        pk=pk,
    )

    if request.method == "POST":
        ingreso.delete()

        messages.success(
            request,
            "Ingreso eliminado correctamente.",
        )

    return redirect(
        "finanzas:finanzas_inicio"
    )


def gasto_crear(request):
    if request.method == "POST":
        form = GastoForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Gasto registrado correctamente.",
            )

            return redirect(
                "finanzas:finanzas_inicio"
            )
    else:
        form = GastoForm()

    context = {
        "form": form,
        "titulo": "Nuevo gasto",
        "boton": "Registrar gasto",
    }

    return render(
        request,
        "finanzas/gasto_form.html",
        context,
    )


def gasto_editar(request, pk):
    gasto = get_object_or_404(
        Gasto,
        pk=pk,
    )

    if request.method == "POST":
        form = GastoForm(
            request.POST,
            instance=gasto,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Gasto actualizado correctamente.",
            )

            return redirect(
                "finanzas:finanzas_inicio"
            )
    else:
        form = GastoForm(
            instance=gasto,
        )

    context = {
        "form": form,
        "gasto": gasto,
        "titulo": "Editar gasto",
        "boton": "Guardar cambios",
    }

    return render(
        request,
        "finanzas/gasto_form.html",
        context,
    )


def gasto_eliminar(request, pk):
    gasto = get_object_or_404(
        Gasto,
        pk=pk,
    )

    if request.method == "POST":
        gasto.delete()

        messages.success(
            request,
            "Gasto eliminado correctamente.",
        )

    return redirect(
        "finanzas:finanzas_inicio"
    )


def cargar_proyectos_cliente(request):
    empresa_id = request.GET.get("empresa_id")

    proyectos = Proyecto.objects.none()

    if empresa_id:
        proyectos = (
            Proyecto.objects
            .filter(empresa_id=empresa_id)
            .order_by("-creado_en")
        )

    datos = [
        {
            "id": proyecto.pk,
            "texto": f"{proyecto.codigo} | {proyecto.nombre}",
        }
        for proyecto in proyectos
    ]

    return JsonResponse(
        {
            "resultados": datos,
        }
    )


def cargar_cotizaciones_cliente(request):
    empresa_id = request.GET.get("empresa_id")

    cotizaciones = Cotizacion.objects.none()

    if empresa_id:
        cotizaciones = (
            Cotizacion.objects
            .filter(oportunidad__empresa_id=empresa_id)
            .order_by("-pk")
        )

    datos = [
        {
            "id": cotizacion.pk,
            "texto": str(cotizacion.numero),
        }
        for cotizacion in cotizaciones
    ]

    return JsonResponse(
        {
            "resultados": datos,
        }
    )

def obtener_proyectos(request):
    empresa_id = request.GET.get("empresa_id")

    proyectos = []

    if empresa_id:
        queryset = (
            Proyecto.objects
            .filter(empresa_id=empresa_id)
            .order_by("-fecha_alta", "nombre")
        )

        proyectos = [
            {
                "id": proyecto.pk,
                "nombre": (
                    f"{proyecto.codigo} - {proyecto.nombre}"
                    if proyecto.codigo
                    else proyecto.nombre
                ),
            }
            for proyecto in queryset
        ]

    return JsonResponse({
        "proyectos": proyectos,
    })


def obtener_cotizaciones(request):
    empresa_id = request.GET.get("empresa_id")

    cotizaciones = []

    if empresa_id:
        queryset = (
            Cotizacion.objects
            .filter(
                oportunidad__empresa_id=empresa_id
            )
            .select_related("oportunidad")
            .order_by("-fecha_emision", "-pk")
        )

        cotizaciones = [
            {
                "id": cotizacion.pk,
                "nombre": (
                    f"{cotizacion.numero} - "
                    f"{cotizacion.total} "
                    f"{cotizacion.moneda}"
                ),
                "monto": str(cotizacion.total),
                "moneda": cotizacion.moneda,
            }
            for cotizacion in queryset
        ]

    return JsonResponse({
        "cotizaciones": cotizaciones,
    })

@user_passes_test(lambda user: user.is_authenticated and user.is_staff)
def bandeja_cobros(request):
    """Bandeja interna de cobros; no expone enlaces ni permite confirmar pagos."""
    estado = request.GET.get("estado", "")
    busqueda = request.GET.get("q", "").strip()
    cobros = Cobro.objects.select_related("ingreso", "ingreso__empresa", "ingreso__cotizacion")
    if estado in Cobro.Estado.values:
        cobros = cobros.filter(estado=estado)
    if busqueda:
        cobros = cobros.filter(
            Q(ingreso__concepto__icontains=busqueda)
            | Q(ingreso__empresa__razon_social__icontains=busqueda)
            | Q(ingreso__cotizacion__numero__icontains=busqueda)
        )
    cobros = cobros.order_by("ingreso__fecha_vencimiento", "pk")
    hoy = timezone.localdate()
    resumen = cobros.aggregate(
        cantidad=Count("pk"),
        monto_total=Sum("ingreso__monto", filter=Q(ingreso__moneda=Moneda.CLP)),
        monto_pagado=Sum("ingreso__monto", filter=Q(estado=Cobro.Estado.PAGADO, ingreso__moneda=Moneda.CLP)),
        monto_pendiente=Sum("ingreso__monto", filter=Q(ingreso__moneda=Moneda.CLP, estado__in=[
            Cobro.Estado.PENDIENTE, Cobro.Estado.EN_PROCESO, Cobro.Estado.VENCIDO,
        ])),
        monto_vencido=Sum("ingreso__monto", filter=(
            Q(ingreso__moneda=Moneda.CLP) & (
                Q(estado=Cobro.Estado.VENCIDO) |
                Q(estado=Cobro.Estado.PENDIENTE, ingreso__fecha_vencimiento__lt=hoy)
            )
        )),
    )
    resumen = {clave: valor or 0 for clave, valor in resumen.items()}
    return render(request, "finanzas/bandeja_cobros.html", {
        "resumen": resumen,
        "cobros": cobros[:200],
        "estados": Cobro.Estado.choices,
        "estado_seleccionado": estado,
        "busqueda": busqueda,
        "hoy": hoy,
    })


@user_passes_test(lambda user: user.is_authenticated and user.is_staff)
def vista_previa_cobros(request, cotizacion_pk):
    """Vista previa solamente: ninguna escritura de cobros ni ingresos."""
    cotizacion = get_object_or_404(
        Cotizacion.objects.select_related("oportunidad", "oportunidad__empresa"),
        pk=cotizacion_pk,
    )
    fecha_texto = request.GET.get("inicio", "")
    filas, error = [], None
    incluir_mantencion = request.GET.get("mantencion") == "1"
    if fecha_texto:
        try:
            fecha = date.fromisoformat(fecha_texto)
            filas = previsualizar_plan(cotizacion, fecha, incluir_mantencion)
        except (ValueError, ValidationError) as exc:
            error = str(exc)
    return render(request, "finanzas/preview_plan_cobros.html", {
        "cotizacion": cotizacion,
        "fecha_texto": fecha_texto,
        "incluir_mantencion": incluir_mantencion,
        "filas": filas,
        "error": error,
        "plan_existente": Ingreso.objects.filter(cotizacion=cotizacion).exists(),
    })


@require_POST
@user_passes_test(lambda user: user.is_authenticated and user.is_staff)
def confirmar_cobros_cotizacion(request, cotizacion_pk):
    """Solo POST autenticado; recalcula los importes en servidor."""
    fecha_texto = request.POST.get("inicio", "")
    incluir_mantencion = request.POST.get("mantencion") == "1"
    try:
        fecha_inicio = date.fromisoformat(fecha_texto)
        creados = confirmar_plan_cobros(cotizacion_pk, fecha_inicio, incluir_mantencion)
    except (ValueError, ValidationError) as exc:
        messages.error(request, f"No se generaron cobros: {exc}")
        return redirect("finanzas:vista_previa_cobros", cotizacion_pk=cotizacion_pk)
    messages.success(request, f"Se generaron {len(creados)} cobros pendientes correctamente.")
    return redirect("finanzas:bandeja_cobros")
