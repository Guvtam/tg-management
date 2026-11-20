"""Cobros individuales asociados a ingresos existentes de TG Management."""
import secrets
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


def generar_token():
    return secrets.token_urlsafe(32)


class Cobro(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        EN_PROCESO = "en_proceso", "En proceso"
        PAGADO = "pagado", "Pagado"
        VENCIDO = "vencido", "Vencido"
        ANULADO = "anulado", "Anulado"

    ingreso = models.OneToOneField(
        "finanzas.Ingreso", on_delete=models.PROTECT, related_name="cobro",
    )
    token = models.CharField(max_length=64, unique=True, default=generar_token, editable=False)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    referencia_proveedor = models.CharField(max_length=150, blank=True, db_index=True)
    proveedor = models.CharField(max_length=40, blank=True)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creado_en"]
        verbose_name = "Cobro"
        verbose_name_plural = "Cobros"

    def __str__(self):
        return f"Cobro {self.pk} · {self.ingreso.concepto}"

    def clean(self):
        if self.estado == self.Estado.PAGADO and not self.fecha_confirmacion:
            raise ValidationError({"fecha_confirmacion": "Un pago requiere confirmación verificable del proveedor."})

    @property
    def vencido(self):
        return (
            self.estado == self.Estado.PENDIENTE
            and bool(self.ingreso.fecha_vencimiento)
            and self.ingreso.fecha_vencimiento < timezone.localdate()
        )
