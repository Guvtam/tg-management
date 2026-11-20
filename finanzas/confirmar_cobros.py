"""Confirmación transaccional e idempotente de un calendario de cobros."""
from datetime import date

from django.core.exceptions import ValidationError
from django.db import transaction

from cotizaciones.models import Cotizacion
from .models import Cobro, Ingreso
from .plan_cobros import previsualizar_plan


@transaction.atomic
def confirmar_plan_cobros(cotizacion_id, fecha_inicio, incluir_mantencion=False):
    """Crea todos los ingresos y cobros o ninguno; nunca duplica un plan."""
    cotizacion = (
        Cotizacion.objects.select_for_update()
        .select_related("oportunidad", "oportunidad__empresa")
        .get(pk=cotizacion_id)
    )
    if not isinstance(fecha_inicio, date):
        raise ValidationError("La fecha de inicio no es válida.")
    if Ingreso.objects.filter(cotizacion=cotizacion).exists():
        raise ValidationError(
            "La cotización ya tiene ingresos asociados. Revisa Finanzas antes de generar un plan."
        )
    filas = previsualizar_plan(cotizacion, fecha_inicio, incluir_mantencion)
    empresa = cotizacion.oportunidad.empresa
    creados = []
    for fila in filas:
        ingreso = Ingreso.objects.create(
            empresa=empresa,
            cotizacion=cotizacion,
            concepto=f"{cotizacion.numero} · {fila['concepto']}",
            monto=fila["monto"],
            moneda=Ingreso._meta.get_field("moneda").default,
            fecha_emision=fecha_inicio,
            fecha_vencimiento=fila["fecha"],
            estado=Ingreso.Estado.PENDIENTE,
            observaciones="Generado desde calendario de cobros de cotización.",
        )
        creados.append(Cobro.objects.create(ingreso=ingreso))
    return creados
