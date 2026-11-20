"""Reglas de negocio para preparar cobros; no inicia transacciones bancarias."""
from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError


def distribuir_cuotas(total, cantidad):
    """Divide CLP en cuotas enteras sin perder pesos por redondeo."""
    if isinstance(total, bool) or isinstance(cantidad, bool):
        raise ValidationError("Monto y cantidad deben ser números válidos.")
    try:
        total = Decimal(str(total))
        cantidad = int(cantidad)
    except (TypeError, ValueError, ArithmeticError):
        raise ValidationError("Monto y cantidad deben ser números válidos.")
    if not total.is_finite() or total <= 0 or total != total.to_integral_value():
        raise ValidationError("El monto en CLP debe ser un entero positivo.")
    if not 1 <= cantidad <= 120 or cantidad > total:
        raise ValidationError("Cantidad de cuotas fuera de rango.")
    pesos = int(total)
    base, resto = divmod(pesos, cantidad)
    return [Decimal(base + (1 if i < resto else 0)) for i in range(cantidad)]


def plan_anticipo_cuotas(total, porcentaje_pie, cantidad):
    """Devuelve anticipo y cuotas, respetando la suma exacta del total CLP."""
    try:
        total = Decimal(str(total))
        porcentaje = Decimal(str(porcentaje_pie))
    except (TypeError, ValueError, ArithmeticError):
        raise ValidationError("Monto o porcentaje inválido.")
    if not total.is_finite() or total <= 0 or total != total.to_integral_value():
        raise ValidationError("El monto CLP debe ser un entero positivo.")
    if not porcentaje.is_finite() or not (0 < porcentaje < 100):
        raise ValidationError("El pie debe ser mayor que 0 y menor que 100.")
    pie = (total * porcentaje / 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    if pie <= 0 or pie >= total:
        raise ValidationError("El pie deja un saldo inválido.")
    return pie, distribuir_cuotas(total - pie, cantidad)
