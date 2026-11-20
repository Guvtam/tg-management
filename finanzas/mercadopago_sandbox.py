"""Mercado Pago Checkout Pro test adapter. Real charges are disabled."""
import json
import os
from decimal import Decimal
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from django.core.exceptions import ValidationError

API = "https://api.mercadopago.com"


def sandbox_configured():
    token = os.environ.get("MP_TEST_ACCESS_TOKEN", "")
    # APP_USR- is not proof of a test credential. Require a second,
    # explicit local opt-in before accepting that format.
    allowed_token = token.startswith("TEST-") or (
        token.startswith("APP_USR-")
        and os.environ.get("MP_ALLOW_APP_USR_TEST_TOKEN") == "1"
    )
    return (
        os.environ.get("MP_SANDBOX_ENABLED") == "1"
        and allowed_token
        and bool(os.environ.get("MP_WEBHOOK_SECRET"))
    )


def _request(path, *, payload=None):
    if not sandbox_configured():
        raise ValidationError("Mercado Pago sandbox no está configurado.")
    if not (path.startswith("/checkout/preferences") or path.startswith("/v1/payments/")):
        raise ValidationError("Endpoint no autorizado.")
    headers = {
        "Authorization": "Bearer " + os.environ["MP_TEST_ACCESS_TOKEN"],
        "Content-Type": "application/json",
    }
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = Request(API + path, data=data, headers=headers, method="POST" if data else "GET")
    try:
        with urlopen(req, timeout=12) as response:
            return json.load(response)
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        raise ValidationError("No se pudo completar la operación de prueba con Mercado Pago.") from exc


def crear_preferencia(cobro, *, url_retorno):
    if cobro.estado not in (cobro.Estado.PENDIENTE, cobro.Estado.VENCIDO):
        raise ValidationError("El cobro no está disponible.")
    if cobro.ingreso.moneda != "CLP":
        raise ValidationError("Mercado Pago sandbox admite solo CLP.")
    monto = cobro.ingreso.monto
    if monto <= 0 or monto != monto.to_integral_value():
        raise ValidationError("El monto debe ser un entero positivo.")
    url = urlparse(url_retorno)
    if url.scheme != "https" and url.hostname not in ("localhost", "127.0.0.1"):
        raise ValidationError("El retorno requiere HTTPS.")
    datos = _request("/checkout/preferences", payload={
        "items": [{
            "id": str(cobro.pk),
            "title": cobro.ingreso.concepto[:120],
            "quantity": 1,
            "currency_id": "CLP",
            "unit_price": int(monto),
        }],
        "external_reference": f"tg-cobro-{cobro.pk}",
        "back_urls": {"success": url_retorno, "pending": url_retorno, "failure": url_retorno},
    })
    enlace = datos.get("sandbox_init_point")
    if not enlace or urlparse(enlace).hostname != "sandbox.mercadopago.com":
        raise ValidationError("Mercado Pago no devolvió un enlace sandbox válido.")
    return enlace


def obtener_pago(payment_id):
    if not str(payment_id).isdigit():
        raise ValidationError("Identificador de pago inválido.")
    return _request(f"/v1/payments/{payment_id}")
