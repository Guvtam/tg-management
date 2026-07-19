import os

# Create your models here.
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


def documento_proyecto_upload_to(instance, filename):
    """
    Guarda los documentos organizados por proyecto y categoría.

    Ejemplo:
    proyectos/PRO-2026-00001/contratos/contrato_cliente.pdf
    """
    nombre_archivo = os.path.basename(filename)

    return (
        f"proyectos/"
        f"{instance.proyecto.codigo}/"
        f"{instance.tipo}/"
        f"{nombre_archivo}"
    )

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
        "Fecha Alta",
        blank=True,
        null=True,
    )

    fecha_entrega = models.DateField(
        "Fecha Entrega",
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
    
    def actualizar_porcentaje_avance(self):
        """
        Calcula el avance del proyecto según sus actividades.

        Las actividades canceladas no participan en el cálculo.
        """

        actividades = self.actividades.exclude(
            estado=ActividadProyecto.Estado.CANCELADA
        )

        total_actividades = actividades.count()

        if total_actividades == 0:
            nuevo_porcentaje = 0
        else:
            actividades_completadas = actividades.filter(
                estado=ActividadProyecto.Estado.COMPLETADA
            ).count()

            nuevo_porcentaje = round(
                actividades_completadas * 100 / total_actividades
            )

        type(self).objects.filter(pk=self.pk).update(
            porcentaje_avance=nuevo_porcentaje
        )

        self.porcentaje_avance = nuevo_porcentaje

        return nuevo_porcentaje

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
    
    def save(self, *args, **kwargs):
        proyecto_anterior_id = None

        if self.pk:
            proyecto_anterior_id = (
                type(self).objects
                .filter(pk=self.pk)
                .values_list("proyecto_id", flat=True)
                .first()
            )

        super().save(*args, **kwargs)

        self.proyecto.actualizar_porcentaje_avance()

        if (
            proyecto_anterior_id
            and proyecto_anterior_id != self.proyecto_id
        ):
            proyecto_anterior = Proyecto.objects.filter(
                pk=proyecto_anterior_id
            ).first()

            if proyecto_anterior:
                proyecto_anterior.actualizar_porcentaje_avance()


    def delete(self, *args, **kwargs):
        proyecto = self.proyecto

        resultado = super().delete(*args, **kwargs)

        proyecto.actualizar_porcentaje_avance()

        return resultado
    

class DocumentoProyecto(models.Model):
    class Tipo(models.TextChoices):
        MINUTA = "minuta", "Minuta de reunión"
        REQUERIMIENTO = "requerimiento", "Requerimiento"
        CONTRATO = "contrato", "Contrato"
        PROPUESTA_TECNICA = "propuesta_tecnica", "Propuesta técnica"
        PROPUESTA_ECONOMICA = "propuesta_economica", "Propuesta económica"
        ORDEN_COMPRA = "orden_compra", "Orden de compra"
        INFORME = "informe", "Informe"
        ACTA_ENTREGA = "acta_entrega", "Acta de entrega"
        PLANO = "plano", "Plano"
        CERTIFICADO = "certificado", "Certificado"
        CORREO = "correo", "Correo o comunicación"
        OTRO = "otro", "Otro documento"

    proyecto = models.ForeignKey(
        "Proyecto",
        verbose_name="Proyecto",
        on_delete=models.CASCADE,
        related_name="documentos",
    )

    nombre = models.CharField(
        "Nombre del documento",
        max_length=200,
    )

    tipo = models.CharField(
        "Tipo de documento",
        max_length=30,
        choices=Tipo.choices,
        default=Tipo.OTRO,
    )

    descripcion = models.TextField(
        "Descripción",
        blank=True,
    )

    archivo = models.FileField(
        "Archivo",
        upload_to=documento_proyecto_upload_to,
    )

    cargado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Cargado por",
        on_delete=models.SET_NULL,
        related_name="documentos_proyecto_cargados",
        blank=True,
        null=True,
    )

    creado_en = models.DateTimeField(
        "Fecha de carga",
        auto_now_add=True,
    )

    actualizado_en = models.DateTimeField(
        "Última modificación",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Documento del proyecto"
        verbose_name_plural = "Documentos del proyecto"
        ordering = ["-creado_en"]

    def __str__(self):
        return f"{self.proyecto.codigo} - {self.nombre}"

    @property
    def nombre_archivo(self):
        return os.path.basename(self.archivo.name)

    @property
    def extension(self):
        nombre = self.nombre_archivo
        return os.path.splitext(nombre)[1].lower()

    @property
    def es_pdf(self):
        return self.extension == ".pdf"

    @property
    def es_imagen(self):
        return self.extension in {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp",
        }

    @property
    def es_visualizable(self):
        return self.es_pdf or self.es_imagen