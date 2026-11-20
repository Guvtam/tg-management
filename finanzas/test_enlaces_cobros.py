from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from crm.models import Empresa
from finanzas.models import Cobro, Ingreso


class EnlacesCobroTests(TestCase):
    def setUp(self):
        empresa = Empresa.objects.create(razon_social="Cliente de prueba")
        ingreso = Ingreso.objects.create(
            empresa=empresa, concepto="Cuota desarrollo 1/12",
            monto=Decimal("60000"), moneda="CLP",
            fecha_emision=timezone.localdate(),
            fecha_vencimiento=timezone.localdate() + timedelta(days=5),
        )
        self.cobro = Cobro.objects.create(ingreso=ingreso)
        self.url = reverse("finanzas:detalle_cobro_publico", args=[self.cobro.token])

    def test_link_access_without_login_and_read_only(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cuota desarrollo 1/12")
        self.assertContains(response, "60000")
        self.assertContains(response, "no recibe pagos")
        self.assertEqual(response["Cache-Control"], "no-store, private")
        self.assertEqual(response["Referrer-Policy"], "no-referrer")
        self.assertIn("noindex", response["X-Robots-Tag"])
        self.cobro.refresh_from_db()
        self.assertEqual(self.cobro.estado, Cobro.Estado.PENDIENTE)

    def test_unknown_token_is_not_found(self):
        response = self.client.get(
            reverse("finanzas:detalle_cobro_publico", args=["token-inexistente"])
        )
        self.assertEqual(response.status_code, 404)

    def test_post_does_not_change_payment_status(self):
        response = self.client.post(self.url, {"estado": "pagado"})
        self.cobro.refresh_from_db()
        self.assertEqual(self.cobro.estado, Cobro.Estado.PENDIENTE)
        self.assertNotEqual(response.status_code, 500)

    def test_link_does_not_show_customer_identity(self):
        response = self.client.get(self.url)
        self.assertNotContains(response, "Cliente de prueba")
