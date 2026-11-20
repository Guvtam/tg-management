"""Previsualización de cobros: no escribe ingresos ni realiza pagos."""
from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError

from .cobros_service import plan_anticipo_cuotas


def agregar_meses(fecha, meses):
    indice = fecha.year * 12 + fecha.month - 1 + meses
    anio, mes = divmod(indice, 12)
    mes += 1
    return date(anio, mes, min(fecha.day, monthrange(anio, mes)[1]))


def previsualizar_plan(cotizacion, fecha_inicio, incluir_mantencion=False):
    """Plan en CLP a partir de modalidad configurada; fechas explícitas."""
    if cotizacion.estado != cotizacion.Estado.APROBADA:
        raise ValidationError("La cotización debe estar aprobada.")
    if cotizacion.moneda != cotizacion.Moneda.CLP:
        raise ValidationError("Por ahora solo se admiten cotizaciones en CLP.")
    if not isinstance(fecha_inicio, date):
        raise ValidationError("Debes indicar una fecha de inicio válida.")
    try:
        modalidad = cotizacion.configuracion_modalidades_pago
    except cotizacion.__class__.configuracion_modalidades_pago.RelatedObjectDoesNotExist:
        raise ValidationError("Configura primero las modalidades de pago.")
    if not modalidad.mostrar_plan_12_meses:
        raise ValidationError("El plan de 12 cuotas no está habilitado.")

    total = cotizacion.total
    if total != total.to_integral_value() or total <= 0:
        raise ValidationError("El total de la cotización debe ser CLP entero positivo.")
    pie, cuotas = plan_anticipo_cuotas(total, modalidad.porcentaje_pie, 12)
    mantencion = Decimal(modalidad.mantencion_mensual)
    if incluir_mantencion and (mantencion < 0 or mantencion != mantencion.to_integral_value()):
        raise ValidationError("La mantención mensual debe expresarse en pesos enteros.")
    filas = [{"concepto": "Pie inicial", "fecha": fecha_inicio, "monto": pie, "tipo": "pie"}]
    for indice, cuota in enumerate(cuotas, start=1):
        vencimiento = agregar_meses(fecha_inicio, indice)
        filas.append({"concepto": f"Cuota desarrollo {indice}/12", "fecha": vencimiento, "monto": cuota, "tipo": "cuota"})
        if incluir_mantencion and mantencion > 0:
            filas.append({"concepto": f"Mantención y soporte {indice}/12", "fecha": vencimiento, "monto": mantencion, "tipo": "mantencion"})
    return filas
