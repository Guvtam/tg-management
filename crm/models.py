# Create your models here.
from django.conf import settings
from django.db import models


class Empresa(models.Model):
    class TipoEmpresa(models.TextChoices):
        PROSPECTO = "PROSPECTO", "Prospecto"
        CLIENTE = "CLIENTE", "Cliente"
        PROVEEDOR = "PROVEEDOR", "Proveedor"
        PARTNER = "PARTNER", "Partner"

    class EstadoEmpresa(models.TextChoices):
        ACTIVA = "ACTIVA", "Activa"
        INACTIVA = "INACTIVA", "Inactiva"

    razon_social = models.CharField(
        "Razón social",
        max_length=200,
    )
    nombre_fantasia = models.CharField(
        "Nombre de fantasía",
        max_length=200,
        blank=True,
    )
    rut = models.CharField(
        "RUT",
        max_length=20,
        blank=True,
        unique=True,
        null=True,
    )
    tipo = models.CharField(
        "Tipo de empresa",
        max_length=20,
        choices=TipoEmpresa.choices,
        default=TipoEmpresa.PROSPECTO,
    )
    rubro = models.CharField(
        "Rubro",
        max_length=150,
        blank=True,
    )
    sitio_web = models.URLField(
        "Sitio web",
        blank=True,
    )
    telefono = models.CharField(
        "Teléfono",
        max_length=30,
        blank=True,
    )
    email = models.EmailField(
        "Correo electrónico",
        blank=True,
    )
    direccion = models.CharField(
        "Dirección",
        max_length=250,
        blank=True,
    )
    comuna = models.CharField(
        "Comuna",
        max_length=100,
        blank=True,
    )
    region = models.CharField(
        "Región",
        max_length=100,
        blank=True,
    )
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=EstadoEmpresa.choices,
        default=EstadoEmpresa.ACTIVA,
    )
    observaciones = models.TextField(
        "Observaciones",
        blank=True,
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Creado por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="empresas_creadas",
    )
    fecha_creacion = models.DateTimeField(
        "Fecha de creación",
        auto_now_add=True,
    )
    fecha_actualizacion = models.DateTimeField(
        "Última actualización",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ["razon_social"]

    def __str__(self):
        return self.nombre_fantasia or self.razon_social


class Contacto(models.Model):
    empresa = models.ForeignKey(
        Empresa,
        verbose_name="Empresa",
        on_delete=models.CASCADE,
        related_name="contactos",
    )
    nombres = models.CharField(
        "Nombres",
        max_length=100,
    )
    apellidos = models.CharField(
        "Apellidos",
        max_length=100,
        blank=True,
    )
    cargo = models.CharField(
        "Cargo",
        max_length=120,
        blank=True,
    )
    email = models.EmailField(
        "Correo electrónico",
        blank=True,
    )
    telefono = models.CharField(
        "Teléfono",
        max_length=30,
        blank=True,
    )
    es_contacto_principal = models.BooleanField(
        "Contacto principal",
        default=False,
    )
    activo = models.BooleanField(
        "Activo",
        default=True,
    )
    observaciones = models.TextField(
        "Observaciones",
        blank=True,
    )
    fecha_creacion = models.DateTimeField(
        "Fecha de creación",
        auto_now_add=True,
    )
    fecha_actualizacion = models.DateTimeField(
        "Última actualización",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Contacto"
        verbose_name_plural = "Contactos"
        ordering = ["empresa", "nombres", "apellidos"]

    def __str__(self):
        nombre_completo = f"{self.nombres} {self.apellidos}".strip()
        return f"{nombre_completo} — {self.empresa}"


class Oportunidad(models.Model):
    class Etapa(models.TextChoices):
        NUEVA = "NUEVA", "Nueva"
        CONTACTADA = "CONTACTADA", "Contactada"
        REQUERIMIENTOS = "REQUERIMIENTOS", "Levantamiento de requerimientos"
        PROPUESTA = "PROPUESTA", "Propuesta enviada"
        NEGOCIACION = "NEGOCIACION", "Negociación"
        GANADA = "GANADA", "Ganada"
        PERDIDA = "PERDIDA", "Perdida"
        PAUSADA = "PAUSADA", "Pausada"

    class Prioridad(models.TextChoices):
        BAJA = "BAJA", "Baja"
        MEDIA = "MEDIA", "Media"
        ALTA = "ALTA", "Alta"
        URGENTE = "URGENTE", "Urgente"

    titulo = models.CharField(
        "Nombre de la oportunidad",
        max_length=200,
    )
    empresa = models.ForeignKey(
        Empresa,
        verbose_name="Empresa",
        on_delete=models.PROTECT,
        related_name="oportunidades",
    )
    contacto = models.ForeignKey(
        Contacto,
        verbose_name="Contacto",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="oportunidades",
    )
    descripcion = models.TextField(
        "Descripción",
        blank=True,
    )
    servicio_interes = models.CharField(
        "Servicio de interés",
        max_length=150,
        blank=True,
    )
    etapa = models.CharField(
        "Etapa",
        max_length=30,
        choices=Etapa.choices,
        default=Etapa.NUEVA,
    )
    prioridad = models.CharField(
        "Prioridad",
        max_length=20,
        choices=Prioridad.choices,
        default=Prioridad.MEDIA,
    )
    valor_estimado = models.DecimalField(
        "Valor estimado",
        max_digits=14,
        decimal_places=2,
        default=0,
    )
    probabilidad = models.PositiveSmallIntegerField(
        "Probabilidad de cierre (%)",
        default=10,
    )
    fecha_estimada_cierre = models.DateField(
        "Fecha estimada de cierre",
        null=True,
        blank=True,
    )
    motivo_perdida = models.TextField(
        "Motivo de pérdida",
        blank=True,
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Responsable",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="oportunidades_asignadas",
    )
    fecha_creacion = models.DateTimeField(
        "Fecha de creación",
        auto_now_add=True,
    )
    fecha_actualizacion = models.DateTimeField(
        "Última actualización",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Oportunidad"
        verbose_name_plural = "Oportunidades"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"{self.titulo} — {self.empresa}"


class Actividad(models.Model):
    class TipoActividad(models.TextChoices):
        LLAMADA = "LLAMADA", "Llamada"
        CORREO = "CORREO", "Correo electrónico"
        REUNION = "REUNION", "Reunión"
        TAREA = "TAREA", "Tarea"
        WHATSAPP = "WHATSAPP", "WhatsApp"
        OTRO = "OTRO", "Otro"

    class EstadoActividad(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        COMPLETADA = "COMPLETADA", "Completada"
        CANCELADA = "CANCELADA", "Cancelada"

    oportunidad = models.ForeignKey(
        Oportunidad,
        verbose_name="Oportunidad",
        on_delete=models.CASCADE,
        related_name="actividades",
    )
    tipo = models.CharField(
        "Tipo de actividad",
        max_length=20,
        choices=TipoActividad.choices,
        default=TipoActividad.TAREA,
    )
    asunto = models.CharField(
        "Asunto",
        max_length=200,
    )
    descripcion = models.TextField(
        "Descripción",
        blank=True,
    )
    fecha_programada = models.DateTimeField(
        "Fecha programada",
    )
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=EstadoActividad.choices,
        default=EstadoActividad.PENDIENTE,
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Responsable",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actividades_asignadas",
    )
    resultado = models.TextField(
        "Resultado",
        blank=True,
    )
    fecha_creacion = models.DateTimeField(
        "Fecha de creación",
        auto_now_add=True,
    )
    fecha_actualizacion = models.DateTimeField(
        "Última actualización",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"
        ordering = ["fecha_programada","-fecha_creacion",]

    def __str__(self):
        return f"{self.get_tipo_display()}: {self.asunto}"