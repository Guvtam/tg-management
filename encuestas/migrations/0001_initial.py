# Generated for TG Management / Django 5.2
import uuid

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("crm", "0002_alter_actividad_options"),
        ("proyectos", "0006_documentoproyecto"),
    ]

    operations = [
        migrations.CreateModel(
            name="EncuestaSatisfaccion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("token", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("estado", models.CharField(choices=[("pendiente", "Pendiente"), ("enviada", "Enviada"), ("respondida", "Respondida"), ("vencida", "Vencida"), ("anulada", "Anulada")], default="pendiente", max_length=20, verbose_name="Estado")),
                ("fecha_vencimiento", models.DateField(blank=True, null=True, verbose_name="Fecha de vencimiento")),
                ("fecha_envio", models.DateTimeField(blank=True, null=True, verbose_name="Fecha de envío")),
                ("fecha_respuesta", models.DateTimeField(blank=True, null=True, verbose_name="Fecha de respuesta")),
                ("satisfaccion_general", models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name="Satisfacción general")),
                ("calidad_solucion", models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name="Calidad de la solución")),
                ("comunicacion", models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name="Comunicación durante el proyecto")),
                ("cumplimiento_plazos", models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name="Cumplimiento de plazos")),
                ("recomendacion", models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)], verbose_name="Probabilidad de recomendación")),
                ("cumplimiento_expectativas", models.CharField(blank=True, choices=[("completamente", "Sí, completamente"), ("parcialmente", "Parcialmente"), ("no", "No")], max_length=20, verbose_name="Cumplimiento de expectativas")),
                ("aspectos_valorados", models.TextField(blank=True, verbose_name="Aspectos más valorados")),
                ("aspectos_mejora", models.TextField(blank=True, verbose_name="Aspectos por mejorar")),
                ("testimonio", models.TextField(blank=True, verbose_name="Testimonio")),
                ("autoriza_testimonio", models.BooleanField(default=False, verbose_name="Autoriza uso del testimonio")),
                ("creado_en", models.DateTimeField(auto_now_add=True, verbose_name="Creado")),
                ("actualizado_en", models.DateTimeField(auto_now=True, verbose_name="Actualizado")),
                ("contacto", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="encuestas_satisfaccion", to="crm.contacto", verbose_name="Contacto")),
                ("creado_por", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="encuestas_satisfaccion_creadas", to=settings.AUTH_USER_MODEL, verbose_name="Creado por")),
                ("empresa", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="encuestas_satisfaccion", to="crm.empresa", verbose_name="Cliente")),
                ("proyecto", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="encuesta_satisfaccion", to="proyectos.proyecto", verbose_name="Proyecto")),
            ],
            options={"verbose_name": "Encuesta de satisfacción", "verbose_name_plural": "Encuestas de satisfacción", "ordering": ["-creado_en"]},
        ),
    ]
