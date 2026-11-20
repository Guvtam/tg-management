from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from finanzas.cobros_service import distribuir_cuotas, plan_anticipo_cuotas


class CobrosServiceTests(SimpleTestCase):
    def test_twelve_installments_exact_total(self):
        cuotas = distribuir_cuotas(720000, 12)
        self.assertEqual(cuotas, [Decimal("60000")] * 12)
        self.assertEqual(sum(cuotas), Decimal("720000"))

    def test_remainder_is_distributed_without_loss(self):
        cuotas = distribuir_cuotas(100, 3)
        self.assertEqual(cuotas, [Decimal("34"), Decimal("33"), Decimal("33")])
        self.assertEqual(sum(cuotas), Decimal("100"))

    def test_down_payment_and_installments(self):
        pie, cuotas = plan_anticipo_cuotas(1200000, 40, 12)
        self.assertEqual(pie, Decimal("480000"))
        self.assertEqual(sum(cuotas), Decimal("720000"))

    def test_invalid_inputs_are_rejected(self):
        for monto, cantidad in [(0, 3), (-100, 3), (100, 0), (100, 101), ("nan", 3), (100.5, 2)]:
            with self.subTest(monto=monto, cantidad=cantidad):
                with self.assertRaises(ValidationError):
                    distribuir_cuotas(monto, cantidad)

    def test_invalid_down_payment_is_rejected(self):
        for porcentaje in [0, 100, -5, "nan"]:
            with self.subTest(porcentaje=porcentaje):
                with self.assertRaises(ValidationError):
                    plan_anticipo_cuotas(1000, porcentaje, 12)
