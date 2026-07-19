import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class EncuestaSatisfaccion(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        ENVIADA = "enviada", "Enviada"
        RESPONDIDA = "respondida", "Respondida"
        VENCIDA = "vencida", "Vencida"
        ANULADA = "anulada", "Anulada"

    class CumplimientoExpectativas(models.TextChoices):
        COMPLETAMENTE = "completamente", "Sí, completamente"
        PARCIALMENTE = "parcialmente", "Parcialmente"
        NO = "no", "No"

    proyecto = models.OneToOneField(
        "proyectos.Proyecto",
        on_delete=models.CASCADE,
        related_name="encuesta_satisfaccion",
        verbose_name="Proyecto",
    )
    empresa = models.ForeignKey(
        "crm.Empresa",
        on_delete=models.PROTECT,
        related_name="encuestas_satisfaccion",
        verbose_name="Cliente",
    )
    contacto = models.ForeignKey(
        "crm.Contacto",
        on_delete=models.SET_NULL,
        related_name="encuestas_satisfaccion",
        verbose_name="Contacto",
        null=True,
        blank=True,
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    estado = models.CharField(
        "Estado", max_length=20, choices=Estado.choices, default=Estado.PENDIENTE
    )
    fecha_vencimiento = models.DateField("Fecha de vencimiento", null=True, blank=True)
    fecha_envio = models.DateTimeField("Fecha de envío", null=True, blank=True)
    fecha_respuesta = models.DateTimeField("Fecha de respuesta", null=True, blank=True)

    satisfaccion_general = models.PositiveSmallIntegerField(
        "Satisfacción general",
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    calidad_solucion = models.PositiveSmallIntegerField(
        "Calidad de la solución",
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comunicacion = models.PositiveSmallIntegerField(
        "Comunicación durante el proyecto",
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    cumplimiento_plazos = models.PositiveSmallIntegerField(
        "Cumplimiento de plazos",
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    recomendacion = models.PositiveSmallIntegerField(
        "Probabilidad de recomendación",
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    cumplimiento_expectativas = models.CharField(
        "Cumplimiento de expectativas",
        max_length=20,
        choices=CumplimientoExpectativas.choices,
        blank=True,
    )
    aspectos_valorados = models.TextField("Aspectos más valorados", blank=True)
    aspectos_mejora = models.TextField("Aspectos por mejorar", blank=True)
    testimonio = models.TextField("Testimonio", blank=True)
    autoriza_testimonio = models.BooleanField(
        "Autoriza uso del testimonio", default=False
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="encuestas_satisfaccion_creadas",
        verbose_name="Creado por",
        null=True,
        blank=True,
    )
    creado_en = models.DateTimeField("Creado", auto_now_add=True)
    actualizado_en = models.DateTimeField("Actualizado", auto_now=True)

    class Meta:
        verbose_name = "Encuesta de satisfacción"
        verbose_name_plural = "Encuestas de satisfacción"
        ordering = ["-creado_en"]

    def __str__(self):
        return f"Encuesta {self.proyecto.codigo} - {self.empresa}"

    def save(self, *args, **kwargs):
        if self.proyecto_id:
            self.empresa_id = self.proyecto.empresa_id
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("encuestas:detalle", kwargs={"pk": self.pk})

    def get_url_publica(self):
        return reverse("encuestas:responder", kwargs={"token": self.token})

    @property
    def promedio_satisfaccion(self):
        valores = [
            self.satisfaccion_general,
            self.calidad_solucion,
            self.comunicacion,
            self.cumplimiento_plazos,
        ]
        valores = [valor for valor in valores if valor is not None]
        return round(sum(valores) / len(valores), 1) if valores else None

    @property
    def categoria_nps(self):
        if self.recomendacion is None:
            return ""
        if self.recomendacion >= 9:
            return "Promotor"
        if self.recomendacion >= 7:
            return "Pasivo"
        return "Detractor"

    @property
    def respondida(self):
        return self.estado == self.Estado.RESPONDIDA
