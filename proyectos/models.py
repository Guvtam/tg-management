from django.db import models

# Create your models here.
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Proyecto(models.Model):
    class Estado(models.TextChoices):
        PLANIFICADO = "planificado", "Planificado"
        EN_CURSO = "en_curso", "En curso"
        PAUSADO = "pausado", "Pausado"
        FINALIZADO = "finalizado", "Finalizado"
        CANCELADO = "cancelado", "Cancelado"

    class Prioridad(models.TextChoices):
        BAJA = "baja", "Baja"
        MEDIA = "media", "Media"
        ALTA = "alta", "Alta"
        URGENTE = "urgente", "Urgente"

    codigo = models.CharField(
        "Código",
        max_length=30,
        unique=True,
        blank=True,
        editable=False,
    )

    nombre = models.CharField(
        "Nombre del proyecto",
        max_length=200,
    )

    empresa = models.ForeignKey(
        "crm.Empresa",
        on_delete=models.PROTECT,
        related_name="proyectos",
        verbose_name="Empresa",
    )

    cotizacion = models.ForeignKey(
        "cotizaciones.Cotizacion",
        on_delete=models.SET_NULL,
        related_name="proyectos",
        verbose_name="Cotización",
        blank=True,
        null=True,
    )

    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="proyectos_responsable",
        verbose_name="Responsable",
        blank=True,
        null=True,
    )

    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=Estado.choices,
        default=Estado.PLANIFICADO,
    )

    prioridad = models.CharField(
        "Prioridad",
        max_length=20,
        choices=Prioridad.choices,
        default=Prioridad.MEDIA,
    )

    porcentaje_avance = models.PositiveSmallIntegerField(
        "Porcentaje de avance",
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )

    fecha_alta = models.DateField(
        "Inicio planificado",
        blank=True,
        null=True,
    )

    fecha_entrega = models.DateField(
        "Fin planificado",
        blank=True,
        null=True,
    )

   

    descripcion = models.TextField(
        "Descripción",
        blank=True,
    )

    

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="proyectos_creados",
        blank=True,
        null=True,
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
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"
        ordering = ["-creado_en"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    def save(self, *args, **kwargs):
        generar_codigo = not self.codigo

        super().save(*args, **kwargs)

        if generar_codigo:
            self.codigo = f"PRO-{self.creado_en:%Y}-{self.pk:05d}"

            type(self).objects.filter(
                pk=self.pk
            ).update(
                codigo=self.codigo
            )



class ActividadProyecto(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        EN_CURSO = "en_curso", "En curso"
        COMPLETADA = "completada", "Completada"
        CANCELADA = "cancelada", "Cancelada"

    class Tipo(models.TextChoices):
        REUNION = "reunion", "Reunión"
        LEVANTAMIENTO = "levantamiento", "Levantamiento"
        DESARROLLO = "desarrollo", "Desarrollo"
        CONFIGURACION = "configuracion", "Configuración"
        REVISION = "revision", "Revisión"
        ENTREGA = "entrega", "Entrega"
        SOPORTE = "soporte", "Soporte"
        OTRO = "otro", "Otro"

    proyecto = models.ForeignKey(
        "Proyecto",
        verbose_name="Proyecto",
        on_delete=models.CASCADE,
        related_name="actividades",
    )

    titulo = models.CharField(
        "Actividad",
        max_length=200,
    )

    tipo = models.CharField(
        "Tipo de actividad",
        max_length=30,
        choices=Tipo.choices,
        default=Tipo.DESARROLLO,
    )

    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Responsable",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actividades_proyecto",
    )

    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )

    fecha = models.DateField(
        "Fecha",
        null=True,
        blank=True,
    )

    descripcion = models.TextField(
        "Descripción",
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
        verbose_name = "Actividad del proyecto"
        verbose_name_plural = "Actividades del proyecto"
        ordering = ["estado", "fecha", "-creado_en"]

    def __str__(self):
        return f"{self.proyecto.codigo} - {self.titulo}"