from decimal import Decimal
from django.core.exceptions import ValidationError

from django.conf import settings
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models


class Cotizacion(models.Model):
    class Estado(models.TextChoices):
        BORRADOR = "borrador", "Borrador"
        ENVIADA = "enviada", "Enviada"
        APROBADA = "aprobada", "Aprobada"
        RECHAZADA = "rechazada", "Rechazada"
        VENCIDA = "vencida", "Vencida"
        ANULADA = "anulada", "Anulada"

    class ModalidadPago(models.TextChoices):
        PAGO_UNICO = (
            "pago_unico",
            "Pago único",
        )
        ANTICIPO_SALDO = (
            "anticipo_saldo",
            "Anticipo y pago del saldo",
        )
        ANTICIPO_CUOTAS = (
            "anticipo_cuotas",
            "Anticipo y saldo en cuotas",
        )
        ANTICIPO_CUOTAS_MENSUAL = (
            "anticipo_cuotas_mensual",
            "Anticipo, saldo en cuotas y servicio mensual",
        )
        SOLO_CUOTAS = (
            "solo_cuotas",
            "Pago en cuotas",
        )
        SERVICIO_MENSUAL = (
            "servicio_mensual",
            "Servicio mensual",
        )

    class Moneda(models.TextChoices):
        CLP = "CLP", "Peso chileno"
        UF = "UF", "Unidad de Fomento"
        USD = "USD", "Dólar estadounidense"

    modalidad_pago = models.CharField(
        "Modalidad de pago",
        max_length=40,
        choices=ModalidadPago.choices,
        default=ModalidadPago.PAGO_UNICO,
    )

    porcentaje_anticipo = models.DecimalField(
        "Porcentaje de anticipo",
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
        help_text="Porcentaje inicial que debe pagar el cliente.",
    )

    numero_cuotas = models.PositiveSmallIntegerField(
        "Número de cuotas",
        default=1,
        help_text="Cantidad de cuotas correspondientes al saldo.",
    )

    monto_servicio_mensual = models.DecimalField(
        "Valor del servicio mensual",
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
    )

    meses_servicio = models.PositiveSmallIntegerField(
        "Cantidad de meses del servicio",
        null=True,
        blank=True,
    )

    fecha_inicio_servicio = models.DateField(
        "Fecha de inicio del servicio mensual",
        null=True,
        blank=True,
    )

    numero = models.CharField(
        "Número de cotización",
        max_length=30,
        unique=True,
        blank=True,
    )

    oportunidad = models.ForeignKey(
        "crm.Oportunidad",
        on_delete=models.PROTECT,
        related_name="cotizaciones",
        verbose_name="Oportunidad",
    )

    contacto = models.ForeignKey(
        "crm.Contacto",
        on_delete=models.SET_NULL,
        related_name="cotizaciones",
        verbose_name="Contacto",
        null=True,
        blank=True,
    )

    fecha_emision = models.DateField(
        "Fecha de emisión",
    )

    fecha_vencimiento = models.DateField(
        "Fecha de vencimiento",
        null=True,
        blank=True,
    )

    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=Estado.choices,
        default=Estado.BORRADOR,
    )

    moneda = models.CharField(
        "Moneda",
        max_length=3,
        choices=Moneda.choices,
        default=Moneda.CLP,
    )

    valor_moneda = models.DecimalField(
        "Valor de la moneda",
        max_digits=15,
        decimal_places=4,
        default=Decimal("1.0000"),
        validators=[
            MinValueValidator(Decimal("0.0001")),
        ],
        help_text=(
            "Para CLP utiliza 1. "
            "Para UF o USD registra el valor en pesos."
        ),
    )

    descuento_porcentaje = models.DecimalField(
        "Descuento general (%)",
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
    )

    impuesto_porcentaje = models.DecimalField(
        "Impuesto (%)",
        max_digits=5,
        decimal_places=2,
        default=Decimal("19.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
    )

    condiciones_pago = models.CharField(
        "Condiciones de pago",
        max_length=250,
        blank=True,
    )

    plazo_entrega = models.CharField(
        "Plazo de entrega",
        max_length=250,
        blank=True,
    )

    validez_oferta = models.CharField(
        "Validez de la oferta",
        max_length=150,
        blank=True,
        default="15 días",
    )

    alcance = models.TextField(
        "Alcance",
        blank=True,
    )

    exclusiones = models.TextField(
        "Exclusiones",
        blank=True,
    )

    observaciones = models.TextField(
        "Observaciones",
        blank=True,
    )

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="cotizaciones_creadas",
        null=True,
        blank=True,
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-fecha_emision",
            "-fecha_creacion",
        ]

        verbose_name = "Cotización"
        verbose_name_plural = "Cotizaciones"

    def __str__(self):
        return f"{self.numero} - {self.oportunidad}"
    
    @property
    def monto_anticipo(self):
        if not self.total:
            return Decimal("0.00")

        porcentaje = self.porcentaje_anticipo or Decimal("0.00")

        return (
            self.total * porcentaje / Decimal("100.00")
        ).quantize(Decimal("0.01"))


    @property
    def saldo_despues_anticipo(self):
        if not self.total:
            return Decimal("0.00")

        return (
            self.total - self.monto_anticipo
        ).quantize(Decimal("0.01"))


    @property
    def monto_cuota(self):
        if not self.numero_cuotas:
            return Decimal("0.00")

        return (
            self.saldo_despues_anticipo
            / Decimal(self.numero_cuotas)
        ).quantize(Decimal("0.01"))


    @property
    def total_servicio_mensual(self):
        if not self.monto_servicio_mensual or not self.meses_servicio:
            return Decimal("0.00")

        return (
            self.monto_servicio_mensual
            * Decimal(self.meses_servicio)
        ).quantize(Decimal("0.01"))

    @property
    def subtotal(self):
        return sum(
            (
                item.subtotal
                for item in self.items.all()
            ),
            Decimal("0.00"),
        )

    @property
    def descuento(self):
        return (
            self.subtotal
            * self.descuento_porcentaje
            / Decimal("100")
        )

    @property
    def neto(self):
        return self.subtotal - self.descuento

    @property
    def impuesto(self):
        return (
            self.neto
            * self.impuesto_porcentaje
            / Decimal("100")
        )

    @property
    def total(self):
        return self.neto + self.impuesto

    @property
    def total_clp(self):
        return self.total * self.valor_moneda
    
    def clean(self):
        super().clean()

        errores = {}

        modalidades_con_anticipo = {
            self.ModalidadPago.ANTICIPO_SALDO,
            self.ModalidadPago.ANTICIPO_CUOTAS,
            self.ModalidadPago.ANTICIPO_CUOTAS_MENSUAL,
        }

        modalidades_con_cuotas = {
            self.ModalidadPago.ANTICIPO_CUOTAS,
            self.ModalidadPago.ANTICIPO_CUOTAS_MENSUAL,
            self.ModalidadPago.SOLO_CUOTAS,
        }

        modalidades_con_servicio = {
            self.ModalidadPago.ANTICIPO_CUOTAS_MENSUAL,
            self.ModalidadPago.SERVICIO_MENSUAL,
        }

        if self.porcentaje_anticipo > Decimal("100.00"):
            errores["porcentaje_anticipo"] = (
                "El porcentaje de anticipo no puede ser mayor a 100."
            )

        if self.modalidad_pago in modalidades_con_anticipo:
            if self.porcentaje_anticipo <= Decimal("0.00"):
                errores["porcentaje_anticipo"] = (
                    "Debe indicar un porcentaje de anticipo mayor a cero."
                )

            if self.porcentaje_anticipo >= Decimal("100.00"):
                errores["porcentaje_anticipo"] = (
                    "El anticipo debe ser menor al 100%, porque existe un saldo."
                )
        else:
            self.porcentaje_anticipo = Decimal("0.00")

        if self.modalidad_pago in modalidades_con_cuotas:
            if not self.numero_cuotas or self.numero_cuotas < 1:
                errores["numero_cuotas"] = (
                    "Debe indicar al menos una cuota."
                )
        else:
            self.numero_cuotas = 1

        if self.modalidad_pago in modalidades_con_servicio:
            if not self.monto_servicio_mensual:
                errores["monto_servicio_mensual"] = (
                    "Debe indicar el valor mensual del servicio."
                )

            if not self.meses_servicio or self.meses_servicio < 1:
                errores["meses_servicio"] = (
                    "Debe indicar la cantidad de meses del servicio."
                )

            if not self.fecha_inicio_servicio:
                errores["fecha_inicio_servicio"] = (
                    "Debe indicar la fecha de inicio del servicio mensual."
                )
        else:
            self.monto_servicio_mensual = None
            self.meses_servicio = None
            self.fecha_inicio_servicio = None

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        generar_numero = not self.numero

        super().save(*args, **kwargs)

        if generar_numero:
            self.numero = (
                f"COT-{self.fecha_emision:%Y}-{self.pk:05d}"
            )

            type(self).objects.filter(
                pk=self.pk
            ).update(
                numero=self.numero
            )


class ItemCotizacion(models.Model):
    cotizacion = models.ForeignKey(
        Cotizacion,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Cotización",
    )

    orden = models.PositiveIntegerField(
        "Orden",
        default=1,
    )

    codigo = models.CharField(
        "Código",
        max_length=50,
        blank=True,
    )

    descripcion = models.CharField(
        "Descripción",
        max_length=500,
    )

    detalle = models.TextField(
        "Detalle",
        blank=True,
    )

    cantidad = models.DecimalField(
        "Cantidad",
        max_digits=12,
        decimal_places=2,
        default=Decimal("1.00"),
        validators=[
            MinValueValidator(Decimal("0.01")),
        ],
    )

    unidad = models.CharField(
        "Unidad",
        max_length=30,
        default="Unidad",
    )

    precio_unitario = models.DecimalField(
        "Precio unitario",
        max_digits=15,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
    )

    descuento_porcentaje = models.DecimalField(
        "Descuento (%)",
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
    )

    class Meta:
        ordering = [
            "orden",
            "pk",
        ]

        verbose_name = "Ítem de cotización"
        verbose_name_plural = "Ítems de cotización"

    def __str__(self):
        return self.descripcion

    @property
    def subtotal_bruto(self):
        return self.cantidad * self.precio_unitario

    @property
    def descuento(self):
        return (
            self.subtotal_bruto
            * self.descuento_porcentaje
            / Decimal("100")
        )

    @property
    def subtotal(self):
        return self.subtotal_bruto - self.descuento
    
    def save(self, *args, **kwargs):
        if not self.codigo and self.cotizacion_id:
            ultimo_item = (
                ItemCotizacion.objects
                .filter(cotizacion_id=self.cotizacion_id)
                .exclude(codigo="")
                .order_by("-pk")
                .first()
            )

            siguiente = 1

            if ultimo_item and ultimo_item.codigo:
                try:
                    siguiente = int(
                        ultimo_item.codigo.replace("ITEM-", "")
                    ) + 1
                except ValueError:
                    siguiente = self.cotizacion.items.count() + 1

            self.codigo = f"ITEM-{siguiente:03d}"

        super().save(*args, **kwargs)