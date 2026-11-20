from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from finanzas.plan_cobros import agregar_meses, previsualizar_plan


class CalendarioCobrosTests(SimpleTestCase):
    def cotizacion(self, *, estado="aprobada", moneda="CLP", total=Decimal("1200000")):
        modalidad = SimpleNamespace(
            mostrar_plan_12_meses=True,
            porcentaje_pie=Decimal("40"),
            mantencion_mensual=Decimal("25000"),
        )
        return SimpleNamespace(
            estado=estado,
            moneda=moneda,
            total=total,
            Estado=SimpleNamespace(APROBADA="aprobada"),
            Moneda=SimpleNamespace(CLP="CLP"),
            configuracion_modalidades_pago=modalidad,
        )

    def test_february_and_month_end(self):
        self.assertEqual(agregar_meses(date(2027, 1, 31), 1), date(2027, 2, 28))
        self.assertEqual(agregar_meses(date(2027, 1, 31), 2), date(2027, 3, 31))

    def test_preview_without_maintenance(self):
        filas = previsualizar_plan(self.cotizacion(), date(2026, 12, 1))
        self.assertEqual(len(filas), 13)
        self.assertEqual(filas[0]["monto"], Decimal("480000"))
        self.assertEqual(sum(f["monto"] for f in filas), Decimal("1200000"))
        self.assertEqual(filas[1]["fecha"], date(2027, 1, 1))

    def test_preview_with_maintenance(self):
        filas = previsualizar_plan(self.cotizacion(), date(2026, 12, 1), True)
        self.assertEqual(len(filas), 25)
        self.assertEqual(sum(f["monto"] for f in filas), Decimal("1500000"))

    def test_reject_unapproved_or_foreign_currency(self):
        for kwargs in ({"estado": "borrador"}, {"moneda": "UF"}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValidationError):
                    previsualizar_plan(self.cotizacion(**kwargs), date(2026, 12, 1))
