from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from cotizaciones.models import Cotizacion, ItemCotizacion
from crm.models import Empresa, Oportunidad

from .models import ModalidadPagoCotizacion


class ModalidadesPagoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        empresa = Empresa.objects.create(razon_social="Pyme de Prueba")
        oportunidad = Oportunidad.objects.create(titulo="Sitio corporativo", empresa=empresa)
        cls.cotizacion = Cotizacion.objects.create(
            oportunidad=oportunidad,
            fecha_emision=date(2026, 7, 19),
            impuesto_porcentaje=Decimal("0.00"),
        )
        ItemCotizacion.objects.create(
            cotizacion=cls.cotizacion,
            descripcion="Desarrollo",
            cantidad=Decimal("1.00"),
            precio_unitario=Decimal("850000.00"),
        )

    def test_calculos_plan_12_meses(self):
        modalidad = ModalidadPagoCotizacion.objects.create(
            cotizacion=self.cotizacion,
            descuento_pago_unico=Decimal("5.00"),
            mantencion_mensual=Decimal("45000.00"),
        )
        self.assertEqual(modalidad.total_pago_unico, Decimal("807500.00"))
        self.assertEqual(modalidad.monto_pie, Decimal("340000.00"))
        self.assertEqual(modalidad.saldo_financiado, Decimal("510000.00"))
        self.assertEqual(modalidad.cuota_desarrollo, Decimal("42500.00"))
        self.assertEqual(modalidad.cuota_mensual_unica, Decimal("87500.00"))
        self.assertEqual(modalidad.numero_cuotas, 12)

    def test_exige_al_menos_una_modalidad(self):
        modalidad = ModalidadPagoCotizacion(
            cotizacion=self.cotizacion,
            mostrar_pago_unico=False,
            mostrar_plan_12_meses=False,
        )
        with self.assertRaises(ValidationError):
            modalidad.full_clean()

    def test_lista_y_formulario_responden(self):
        self.assertEqual(self.client.get(reverse("modalidades_pago:lista")).status_code, 200)
        self.assertEqual(
            self.client.get(reverse("modalidades_pago:configurar", args=[self.cotizacion.pk])).status_code,
            200,
        )

    def test_guardado_desde_formulario(self):
        response = self.client.post(
            reverse("modalidades_pago:configurar", args=[self.cotizacion.pk]),
            {
                "mostrar_pago_unico": "on",
                "descuento_pago_unico": "5.00",
                "mostrar_plan_12_meses": "on",
                "porcentaje_pie": "40.00",
                "mantencion_mensual": "45000.00",
                "observaciones": "Compromiso de 12 meses.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ModalidadPagoCotizacion.objects.filter(cotizacion=self.cotizacion).exists())
