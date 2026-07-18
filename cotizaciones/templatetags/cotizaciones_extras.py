"""
Filtro de formato de moneda para las cotizaciones.

Instalación:
1. Crea la carpeta cotizaciones/templatetags/ con un __init__.py vacío
   (si no existe todavía).
2. Copia este archivo como cotizaciones/templatetags/cotizaciones_extras.py
3. En el template, agrega arriba de todo: {% load cotizaciones_extras %}
4. Úsalo así: {{ item.subtotal|formato_moneda:cotizacion.moneda }}
"""

from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter(name="formato_moneda")
def formato_moneda(valor, moneda="CLP"):
    """
    Formatea un monto según la moneda de la cotización, con separadores
    al estilo chileno (punto para miles, coma para decimales).

    formato_moneda(1250000, "CLP")  -> "$1.250.000"
    formato_moneda(45.326, "UF")    -> "UF 45,33"
    formato_moneda(1500.5, "USD")   -> "US$ 1.500,50"
    """
    if valor is None or valor == "":
        return ""

    try:
        valor = Decimal(str(valor))
    except (InvalidOperation, ValueError):
        return valor

    if moneda == "UF":
        decimales = 2
        prefijo = "UF "
    elif moneda == "USD":
        decimales = 2
        prefijo = "US$ "
    else:  # CLP por defecto: sin decimales
        decimales = 0
        prefijo = "$"

    cantidad = f"{valor:,.{decimales}f}"

    # cambia el formato en-US (1,234.56) al formato chileno (1.234,56)
    cantidad = cantidad.replace(",", "X").replace(".", ",").replace("X", ".")

    return f"{prefijo}{cantidad}"