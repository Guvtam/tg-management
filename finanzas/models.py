from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Moneda(models.TextChoices):
    CLP = "CLP", "Peso chileno"
    UF = "UF", "Unidad de Fomento"
    USD = "USD", "Dólar estadounidense"


class Ingreso(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        PAGADO = "pagado", "Pagado"
        VENCIDO = "vencido", "Vencido"
        ANULADO = "anulado", "Anulado"

    empresa = models.ForeignKey(
        "crm.Empresa",
        verbose_name="Cliente",
        on_delete=models.PROTECT,
        related_name="ingresos",
    )

    proyecto = models.ForeignKey(
        "proyectos.Proyecto",
        verbose_name="Proyecto",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ingresos",
    )

    cotizacion = models.ForeignKey(
        "cotizaciones.Cotizacion",
        verbose_name="Cotización",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ingresos",
    )

    concepto = models.CharField(
        "Concepto",
        max_length=200,
    )

    monto = models.DecimalField(
        "Monto",
        max_digits=14,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01")),
        ],
    )

    moneda = models.CharField(
        "Moneda",
        max_length=3,
        choices=Moneda.choices,
        default=Moneda.CLP,
    )

    fecha_emision = models.DateField(
        "Fecha de emisión",
    )

    fecha_vencimiento = models.DateField(
        "Fecha de vencimiento",
        null=True,
        blank=True,
    )

    fecha_pago = models.DateField(
        "Fecha de pago",
        null=True,
        blank=True,
    )

    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )

    observaciones = models.TextField(
        "Observaciones",
        blank=True,
    )

    creado_en = models.DateTimeField(
        "Creado",
        auto_now_add=True,
    )

    actualizado_en = models.DateTimeField(
        "Actualizado",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Ingreso"
        verbose_name_plural = "Ingresos"
        ordering = ["-fecha_emision", "-creado_en"]

    def __str__(self):
        return (
            f"{self.concepto} - "
            f"{self.monto} {self.moneda}"
        )


class Gasto(models.Model):
    class Categoria(models.TextChoices):
        SOFTWARE = "software", "Software y licencias"
        HOSTING = "hosting", "Hosting y dominio"
        EQUIPOS = "equipos", "Equipos"
        SERVICIOS = "servicios", "Servicios externos"
        TRANSPORTE = "transporte", "Transporte"
        IMPUESTOS = "impuestos", "Impuestos"
        OTROS = "otros", "Otros"

    proyecto = models.ForeignKey(
        "proyectos.Proyecto",
        verbose_name="Proyecto",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="gastos",
    )

    categoria = models.CharField(
        "Categoría",
        max_length=30,
        choices=Categoria.choices,
        default=Categoria.OTROS,
    )

    proveedor = models.CharField(
        "Proveedor",
        max_length=150,
        blank=True,
    )

    concepto = models.CharField(
        "Concepto",
        max_length=200,
    )

    monto = models.DecimalField(
        "Monto",
        max_digits=14,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01")),
        ],
    )

    moneda = models.CharField(
        "Moneda",
        max_length=3,
        choices=Moneda.choices,
        default=Moneda.CLP,
    )

    fecha = models.DateField(
        "Fecha",
    )

    observaciones = models.TextField(
        "Observaciones",
        blank=True,
    )

    creado_en = models.DateTimeField(
        "Creado",
        auto_now_add=True,
    )

    actualizado_en = models.DateTimeField(
        "Actualizado",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"
        ordering = ["-fecha", "-creado_en"]

    def __str__(self):
        return (
            f"{self.concepto} - "
            f"{self.monto} {self.moneda}"
        )

# Importado al final para registrar el modelo Cobro en Django.
from .cobros import Cobro  # noqa: E402,F401
