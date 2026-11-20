from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from crm.models import Empresa
from finanzas.models import Cobro, Ingreso
from finanzas.mercadopago_sandbox import crear_preferencia, sandbox_configured


class MercadoPagoSandboxTests(TestCase):
    def setUp(self):
        empresa = Empresa.objects.create(razon_social="Empresa test")
        ingreso = Ingreso.objects.create(
            empresa=empresa, concepto="Cuota 1/12",
            monto=Decimal("20000"), moneda="CLP", fecha_emision=date(2026, 11, 20),
        )
        self.cobro = Cobro.objects.create(ingreso=ingreso)
        self.url = reverse("finanzas:iniciar_pago_sandbox", args=[self.cobro.token])

    def test_disabled_by_default(self):
        with patch.dict("os.environ", {}, clear=True):
            response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)
        self.cobro.refresh_from_db()
        self.assertEqual(self.cobro.estado, Cobro.Estado.PENDIENTE)

    def test_app_usr_token_requires_explicit_opt_in(self):
        env = {
            "MP_SANDBOX_ENABLED": "1",
            "MP_TEST_ACCESS_TOKEN": "APP_USR-example",
            "MP_WEBHOOK_SECRET": "fake-test-secret",
        }
        with patch.dict("os.environ", env, clear=True):
            self.assertFalse(sandbox_configured())
            self.assertEqual(self.client.post(self.url).status_code, 403)
        env["MP_ALLOW_APP_USR_TEST_TOKEN"] = "1"
        with patch.dict("os.environ", env, clear=True):
            self.assertTrue(sandbox_configured())
            with patch("finanzas.mercadopago_sandbox._request", return_value={
                "sandbox_init_point": "https://sandbox.mercadopago.com/checkout/pay?pref_id=test"
            }):
                response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].startswith("https://sandbox.mercadopago.com/"))
        self.cobro.refresh_from_db()
        self.assertEqual(self.cobro.estado, Cobro.Estado.PENDIENTE)

    def test_app_usr_opt_in_still_rejects_live_checkout(self):
        env = {
            "MP_SANDBOX_ENABLED": "1",
            "MP_TEST_ACCESS_TOKEN": "APP_USR-example",
            "MP_WEBHOOK_SECRET": "fake-test-secret",
            "MP_ALLOW_APP_USR_TEST_TOKEN": "1",
        }
        with patch.dict("os.environ", env, clear=True):
            with patch("finanzas.mercadopago_sandbox._request", return_value={
                "sandbox_init_point": "https://www.mercadopago.com/checkout/pay"
            }):
                self.assertEqual(self.client.post(self.url).status_code, 400)

    def test_get_does_not_start_checkout(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_mock_checkout_redirects_only_to_sandbox(self):
        env = {
            "MP_SANDBOX_ENABLED": "1",
            "MP_TEST_ACCESS_TOKEN": "TEST-example",
            "MP_WEBHOOK_SECRET": "fake-test-secret",
        }
        with patch.dict("os.environ", env, clear=True):
            with patch("finanzas.mercadopago_sandbox._request", return_value={
                "sandbox_init_point": "https://sandbox.mercadopago.com/checkout/pay?pref_id=abc"
            }) as api:
                response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].startswith("https://sandbox.mercadopago.com/"))
        self.assertEqual(api.call_args.kwargs["payload"]["external_reference"], f"tg-cobro-{self.cobro.pk}")
        self.cobro.refresh_from_db()
        self.assertEqual(self.cobro.estado, Cobro.Estado.PENDIENTE)

    def test_rejects_live_checkout_url(self):
        with patch("finanzas.mercadopago_sandbox._request", return_value={
            "init_point": "https://www.mercadopago.com/checkout"
        }):
            with self.assertRaises(ValidationError):
                crear_preferencia(self.cobro, url_retorno="http://localhost:8000/finanzas/")

    def test_rejects_paid_or_cancelled(self):
        for estado in (Cobro.Estado.PAGADO, Cobro.Estado.ANULADO):
            self.cobro.estado = estado
            with self.assertRaises(ValidationError):
                crear_preferencia(self.cobro, url_retorno="http://localhost:8000/")
