from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from crm.models import Empresa
from finanzas.models import Cobro, Ingreso


class CobroModelTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(
            razon_social="Cliente cobros SpA",
            tipo=Empresa.TipoEmpresa.CLIENTE,
            estado=Empresa.EstadoEmpresa.ACTIVA,
        )
        self.ingreso = Ingreso.objects.create(
            empresa=self.empresa,
            concepto="Cuota de desarrollo",
            monto=Decimal("60000.00"),
            moneda="CLP",
            fecha_emision=timezone.localdate(),
            fecha_vencimiento=timezone.localdate(),
        )

    def test_cobro_generates_unique_opaque_token(self):
        cobro = Cobro.objects.create(ingreso=self.ingreso)
        self.assertGreaterEqual(len(cobro.token), 40)
        self.assertNotEqual(cobro.token, str(self.ingreso.pk))
        self.assertEqual(cobro.estado, Cobro.Estado.PENDIENTE)

    def test_cannot_mark_paid_without_provider_confirmation(self):
        cobro = Cobro(ingreso=self.ingreso, estado=Cobro.Estado.PAGADO)
        with self.assertRaises(ValidationError):
            cobro.full_clean()

    def test_one_cobro_per_ingreso(self):
        from django.db import IntegrityError, transaction
        Cobro.objects.create(ingreso=self.ingreso)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Cobro.objects.create(ingreso=self.ingreso)

    def test_overdue_only_when_pending(self):
        self.ingreso.fecha_vencimiento = timezone.localdate() - timezone.timedelta(days=1)
        self.ingreso.save(update_fields=["fecha_vencimiento"])
        cobro = Cobro.objects.create(ingreso=self.ingreso)
        self.assertTrue(cobro.vencido)
        cobro.estado = Cobro.Estado.ANULADO
        self.assertFalse(cobro.vencido)
