from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from crm.models import Empresa, Oportunidad
from cotizaciones.models import Cotizacion, ItemCotizacion
from modalidades_pago.models import ModalidadPagoCotizacion
from finanzas.confirmar_cobros import confirmar_plan_cobros
from finanzas.models import Cobro, Ingreso


class ConfirmacionCobrosTests(TestCase):
    def setUp(self):
        empresa = Empresa.objects.create(razon_social="Empresa de prueba")
        oportunidad = Oportunidad.objects.create(empresa=empresa, titulo="Desarrollo web")
        self.cotizacion = Cotizacion.objects.create(
            oportunidad=oportunidad,
            fecha_emision=date(2026, 11, 20),
            estado=Cotizacion.Estado.APROBADA,
            moneda=Cotizacion.Moneda.CLP,
            impuesto_porcentaje=Decimal("0"),
        )
        ItemCotizacion.objects.create(
            cotizacion=self.cotizacion,
            descripcion="Desarrollo",
            cantidad=Decimal("1"),
            precio_unitario=Decimal("1200000"),
        )
        ModalidadPagoCotizacion.objects.create(
            cotizacion=self.cotizacion,
            porcentaje_pie=Decimal("40"),
            mantencion_mensual=Decimal("25000"),
        )
        self.url = reverse("finanzas:confirmar_cobros_cotizacion", args=[self.cotizacion.pk])

    def test_creates_exactly_13_pending_records(self):
        cobros = confirmar_plan_cobros(self.cotizacion.pk, date(2026, 12, 1))
        self.assertEqual(len(cobros), 13)
        self.assertEqual(Ingreso.objects.filter(cotizacion=self.cotizacion).count(), 13)
        self.assertEqual(Cobro.objects.filter(ingreso__cotizacion=self.cotizacion).count(), 13)
        self.assertEqual(sum(i.monto for i in Ingreso.objects.filter(cotizacion=self.cotizacion)), Decimal("1200000"))
        self.assertTrue(all(c.estado == Cobro.Estado.PENDIENTE for c in cobros))

    def test_optional_maintenance_creates_25_records(self):
        cobros = confirmar_plan_cobros(self.cotizacion.pk, date(2026, 12, 1), True)
        self.assertEqual(len(cobros), 25)
        self.assertEqual(sum(i.monto for i in Ingreso.objects.filter(cotizacion=self.cotizacion)), Decimal("1500000"))

    def test_second_confirmation_does_not_duplicate(self):
        confirmar_plan_cobros(self.cotizacion.pk, date(2026, 12, 1))
        with self.assertRaises(ValidationError):
            confirmar_plan_cobros(self.cotizacion.pk, date(2026, 12, 1))
        self.assertEqual(Ingreso.objects.filter(cotizacion=self.cotizacion).count(), 13)

    def test_rejects_existing_manual_income(self):
        Ingreso.objects.create(
            empresa=self.cotizacion.oportunidad.empresa,
            cotizacion=self.cotizacion,
            concepto="Anticipo manual",
            monto=Decimal("100"),
            fecha_emision=date(2026, 11, 20),
        )
        with self.assertRaises(ValidationError):
            confirmar_plan_cobros(self.cotizacion.pk, date(2026, 12, 1))
        self.assertEqual(Cobro.objects.count(), 0)

    def test_rejects_draft_without_partial_writes(self):
        self.cotizacion.estado = Cotizacion.Estado.BORRADOR
        self.cotizacion.save(update_fields=["estado"])
        with self.assertRaises(ValidationError):
            confirmar_plan_cobros(self.cotizacion.pk, date(2026, 12, 1))
        self.assertEqual(Ingreso.objects.count(), 0)

    def test_get_does_not_create_cobros(self):
        admin = get_user_model().objects.create_user(username="cobros_admin", password="test", is_staff=True)
        self.client.force_login(admin)
        self.assertEqual(self.client.get(self.url).status_code, 405)
        self.assertEqual(Ingreso.objects.count(), 0)

    def test_staff_post_creates_cobros(self):
        admin = get_user_model().objects.create_user(username="cobros_admin", password="test", is_staff=True)
        self.client.force_login(admin)
        response = self.client.post(self.url, {"inicio": "2026-12-01", "mantencion": "0"})
        self.assertRedirects(response, reverse("finanzas:bandeja_cobros"), fetch_redirect_response=False)
        self.assertEqual(Ingreso.objects.count(), 13)

    def test_anonymous_post_does_not_create_cobros(self):
        self.assertEqual(self.client.post(self.url, {"inicio": "2026-12-01"}).status_code, 302)
        self.assertEqual(Ingreso.objects.count(), 0)
