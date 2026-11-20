from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from crm.models import Empresa
from finanzas.models import Cobro, Ingreso
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CobrosDashboardTests(TestCase):
    def setUp(self):
        self.url = reverse("finanzas:bandeja_cobros")

    def test_anonymous_user_cannot_access_dashboard(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_nonstaff_user_cannot_access_dashboard(self):
        user = get_user_model().objects.create_user(username="operador", password="clave-de-prueba")
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)

    def test_staff_user_can_view_dashboard(self):
        user = get_user_model().objects.create_user(username="administrador", password="clave-de-prueba", is_staff=True)
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bandeja de cobros")

    def test_dashboard_includes_summary_for_empty_records(self):
        user = get_user_model().objects.create_user(
            username="resumen_admin", password="clave-de-prueba", is_staff=True
        )
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["resumen"]["cantidad"], 0)
        self.assertEqual(response.context["resumen"]["monto_pendiente"], 0)
        self.assertContains(response, "Resumen de cobros filtrados")

    def test_summary_amounts_statuses_filters_and_currency(self):
        user = get_user_model().objects.create_user(
            username="resumen_integral", password="clave-de-prueba", is_staff=True
        )
        self.client.force_login(user)
        empresa = Empresa.objects.create(razon_social="Cliente de prueba")
        hoy = timezone.localdate()

        def nuevo(concepto, monto, estado, vencimiento, moneda="CLP"):
            ingreso = Ingreso.objects.create(
                empresa=empresa, concepto=concepto, monto=Decimal(monto),
                moneda=moneda, fecha_emision=hoy, fecha_vencimiento=vencimiento,
            )
            return Cobro.objects.create(ingreso=ingreso, estado=estado)

        nuevo("Plan Alfa", "10000", Cobro.Estado.PENDIENTE, hoy - timedelta(days=1))
        nuevo("Plan Alfa", "20000", Cobro.Estado.PENDIENTE, hoy + timedelta(days=5))
        nuevo("Plan Alfa", "30000", Cobro.Estado.PAGADO, hoy - timedelta(days=2))
        nuevo("Plan Alfa", "40000", Cobro.Estado.ANULADO, hoy - timedelta(days=2))
        nuevo("Plan Alfa", "50000", Cobro.Estado.VENCIDO, hoy - timedelta(days=3))
        nuevo("Plan Alfa", "100", Cobro.Estado.PENDIENTE, hoy, moneda="USD")
        nuevo("Plan Beta", "70000", Cobro.Estado.PENDIENTE, hoy)

        response = self.client.get(self.url, {"q": "Plan Alfa"})
        self.assertEqual(response.status_code, 200)
        resumen = response.context["resumen"]
        self.assertEqual(resumen["cantidad"], 6)
        self.assertEqual(resumen["monto_total"], Decimal("150000"))
        self.assertEqual(resumen["monto_pagado"], Decimal("30000"))
        self.assertEqual(resumen["monto_pendiente"], Decimal("80000"))
        self.assertEqual(resumen["monto_vencido"], Decimal("60000"))

        response = self.client.get(self.url, {"q": "Plan Alfa", "estado": "pendiente"})
        resumen = response.context["resumen"]
        self.assertEqual(resumen["cantidad"], 3)
        self.assertEqual(resumen["monto_total"], Decimal("30000"))
        self.assertEqual(resumen["monto_vencido"], Decimal("10000"))
