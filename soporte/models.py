from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


# SLA de primera respuesta por prioridad, en horas hábiles.
SLA_HORAS_POR_PRIORIDAD = {
    "critica": 4,
    "alta": 8,
    "media": 24,
    "baja": 72,
}


class Ticket(models.Model):
    class Categoria(models.TextChoices):
        INCIDENTE = "incidente", "Incidente / error"
        SOLICITUD_CAMBIO = "solicitud_cambio", "Solicitud de cambio"
        DUDA = "duda", "Duda / consulta"
        MANTENCION = "mantencion", "Mantención programada"
        OTRO = "otro", "Otro"

    class Prioridad(models.TextChoices):
        BAJA = "baja", "Baja"
        MEDIA = "media", "Media"
        ALTA = "alta", "Alta"
        CRITICA = "critica", "Crítica"

    class Estado(models.TextChoices):
        ABIERTO = "abierto", "Abierto"
        EN_PROCESO = "en_proceso", "En proceso"
        ESPERANDO_CLIENTE = "esperando_cliente", "Esperando al cliente"
        RESUELTO = "resuelto", "Resuelto"
        CERRADO = "cerrado", "Cerrado"

    class Canal(models.TextChoices):
        EMAIL = "email", "Correo electrónico"
        WHATSAPP = "whatsapp", "WhatsApp"
        TELEFONO = "telefono", "Teléfono"
        FORMULARIO = "formulario", "Formulario web"
        OTRO = "otro", "Otro"

    codigo = models.CharField(
        "Código",
        max_length=30,
        unique=True,
        blank=True,
        editable=False,
    )

    empresa = models.ForeignKey(
        "crm.Empresa",
        verbose_name="Cliente",
        on_delete=models.PROTECT,
        related_name="tickets",
        null=True,
        blank=True,
    )

    solicitud_web_id = models.UUIDField(null=True, blank=True, unique=True, editable=False)
    nombre_reportante = models.CharField("Nombre del reportante", max_length=120, blank=True)
    correo_reportante = models.EmailField("Correo del reportante", blank=True)

    contacto = models.ForeignKey(
        "crm.Contacto",
        verbose_name="Reportado por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets",
    )

    proyecto = models.ForeignKey(
        "proyectos.Proyecto",
        verbose_name="Proyecto asociado",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets",
    )

    titulo = models.CharField(
        "Título",
        max_length=200,
    )

    descripcion = models.TextField(
        "Descripción",
        blank=True,
    )

    categoria = models.CharField(
        "Categoría",
        max_length=30,
        choices=Categoria.choices,
        default=Categoria.INCIDENTE,
    )

    prioridad = models.CharField(
        "Prioridad",
        max_length=20,
        choices=Prioridad.choices,
        default=Prioridad.MEDIA,
    )

    estado = models.CharField(
        "Estado",
        max_length=30,
        choices=Estado.choices,
        default=Estado.ABIERTO,
    )

    canal = models.CharField(
        "Canal de ingreso",
        max_length=20,
        choices=Canal.choices,
        default=Canal.EMAIL,
    )

    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Responsable",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets_asignados",
    )

    fecha_reporte = models.DateTimeField(
        "Fecha de reporte",
        auto_now_add=True,
    )

    fecha_limite_respuesta = models.DateTimeField(
        "Límite de primera respuesta (SLA)",
        null=True,
        blank=True,
        editable=False,
    )

    fecha_primera_respuesta = models.DateTimeField(
        "Fecha de primera respuesta",
        null=True,
        blank=True,
    )

    fecha_resolucion = models.DateTimeField(
        "Fecha de resolución",
        null=True,
        blank=True,
    )

    horas_dedicadas = models.DecimalField(
        "Horas dedicadas",
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Útil para descontar de la bolsa de horas de mantención mensual.",
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
        verbose_name = "Ticket de soporte"
        verbose_name_plural = "Tickets de soporte"
        ordering = ["-fecha_reporte"]

    def __str__(self):
        return f"{self.codigo} - {self.titulo}"

    @property
    def esta_vencido(self):
        if self.estado in {self.Estado.RESUELTO, self.Estado.CERRADO}:
            return False

        if not self.fecha_limite_respuesta:
            return False

        if self.fecha_primera_respuesta:
            return self.fecha_primera_respuesta > self.fecha_limite_respuesta

        return timezone.now() > self.fecha_limite_respuesta

    def save(self, *args, **kwargs):
        generar_codigo = not self.codigo
        es_nuevo = self._state.adding

        if es_nuevo and not self.fecha_limite_respuesta:
            horas_sla = SLA_HORAS_POR_PRIORIDAD.get(self.prioridad, 24)
            self.fecha_limite_respuesta = timezone.now() + timezone.timedelta(
                hours=horas_sla
            )

        super().save(*args, **kwargs)

        if generar_codigo:
            self.codigo = f"TCK-{self.fecha_reporte:%Y}-{self.pk:05d}"

            type(self).objects.filter(pk=self.pk).update(codigo=self.codigo)


class InteraccionTicket(models.Model):
    class Tipo(models.TextChoices):
        COMENTARIO_INTERNO = "comentario_interno", "Comentario interno"
        RESPUESTA_CLIENTE = "respuesta_cliente", "Respuesta al cliente"
        CAMBIO_ESTADO = "cambio_estado", "Cambio de estado"

    ticket = models.ForeignKey(
        Ticket,
        verbose_name="Ticket",
        on_delete=models.CASCADE,
        related_name="interacciones",
    )

    tipo = models.CharField(
        "Tipo",
        max_length=30,
        choices=Tipo.choices,
        default=Tipo.COMENTARIO_INTERNO,
    )

    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Autor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="interacciones_ticket",
    )

    mensaje = models.TextField(
        "Mensaje",
    )

    fecha_creacion = models.DateTimeField(
        "Fecha",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Interacción de ticket"
        verbose_name_plural = "Interacciones de ticket"
        ordering = ["fecha_creacion"]

    def __str__(self):
        return f"{self.ticket.codigo} - {self.get_tipo_display()}"
