from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


DOS_DECIMALES = Decimal("0.01")


def redondear(valor):
    return Decimal(valor or 0).quantize(DOS_DECIMALES, rounding=ROUND_HALF_UP)


class ModalidadPagoCotizacion(models.Model):
    """Condiciones comerciales opcionales asociadas a una cotización."""

    cotizacion = models.OneToOneField(
        "cotizaciones.Cotizacion",
        on_delete=models.CASCADE,
        related_name="configuracion_modalidades_pago",
        verbose_name="Cotización",
    )
    mostrar_pago_unico = models.BooleanField(
        "Mostrar pago único",
        default=True,
    )
    descuento_pago_unico = models.DecimalField(
        "Descuento por pago único (%)",
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
    )
    mostrar_plan_12_meses = models.BooleanField(
        "Mostrar pie 40% + 12 cuotas",
        default=True,
    )
    porcentaje_pie = models.DecimalField(
        "Pie inicial (%)",
        max_digits=5,
        decimal_places=2,
        default=Decimal("40.00"),
        validators=[
            MinValueValidator(Decimal("0.01")),
            MaxValueValidator(Decimal("99.99")),
        ],
    )
    numero_cuotas = models.PositiveSmallIntegerField(
        "Cantidad de cuotas",
        default=12,
        editable=False,
    )
    mantencion_mensual = models.DecimalField(
        "Mantención y soporte mensual",
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    observaciones = models.TextField(
        "Observaciones comerciales",
        blank=True,
        help_text="Condiciones o aclaraciones que acompañarán las modalidades.",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Modalidad de pago de cotización"
        verbose_name_plural = "Modalidades de pago de cotizaciones"
        ordering = ["-fecha_actualizacion"]

    def __str__(self):
        return f"Modalidades de {self.cotizacion.numero}"

    def clean(self):
        super().clean()
        errores = {}
        if not self.mostrar_pago_unico and not self.mostrar_plan_12_meses:
            errores["mostrar_pago_unico"] = (
                "Debes habilitar al menos una modalidad de pago."
            )
        if self.numero_cuotas != 12:
            errores["numero_cuotas"] = "El plan comercial debe mantenerse en 12 cuotas."
        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        self.numero_cuotas = 12
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def valor_cotizacion(self):
        return redondear(self.cotizacion.total)

    @property
    def descuento_pago_unico_monto(self):
        return redondear(
            self.valor_cotizacion
            * (self.descuento_pago_unico or Decimal("0"))
            / Decimal("100")
        )

    @property
    def total_pago_unico(self):
        return redondear(self.valor_cotizacion - self.descuento_pago_unico_monto)

    @property
    def monto_pie(self):
        return redondear(
            self.valor_cotizacion
            * (self.porcentaje_pie or Decimal("0"))
            / Decimal("100")
        )

    @property
    def saldo_financiado(self):
        return redondear(self.valor_cotizacion - self.monto_pie)

    @property
    def cuota_desarrollo(self):
        return redondear(self.saldo_financiado / Decimal("12"))

    @property
    def cuota_mensual_unica(self):
        return redondear(self.cuota_desarrollo + (self.mantencion_mensual or Decimal("0")))
