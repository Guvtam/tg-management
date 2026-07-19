from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [("cotizaciones", "0002_cotizacion_fecha_inicio_servicio_and_more")]

    operations = [
        migrations.CreateModel(
            name="ModalidadPagoCotizacion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("mostrar_pago_unico", models.BooleanField(default=True, verbose_name="Mostrar pago único")),
                ("descuento_pago_unico", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=5, validators=[django.core.validators.MinValueValidator(Decimal("0.00")), django.core.validators.MaxValueValidator(Decimal("100.00"))], verbose_name="Descuento por pago único (%)")),
                ("mostrar_plan_12_meses", models.BooleanField(default=True, verbose_name="Mostrar pie 40% + 12 cuotas")),
                ("porcentaje_pie", models.DecimalField(decimal_places=2, default=Decimal("40.00"), max_digits=5, validators=[django.core.validators.MinValueValidator(Decimal("0.01")), django.core.validators.MaxValueValidator(Decimal("99.99"))], verbose_name="Pie inicial (%)")),
                ("numero_cuotas", models.PositiveSmallIntegerField(default=12, editable=False, verbose_name="Cantidad de cuotas")),
                ("mantencion_mensual", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14, validators=[django.core.validators.MinValueValidator(Decimal("0.00"))], verbose_name="Mantención y soporte mensual")),
                ("observaciones", models.TextField(blank=True, help_text="Condiciones o aclaraciones que acompañarán las modalidades.", verbose_name="Observaciones comerciales")),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                ("fecha_actualizacion", models.DateTimeField(auto_now=True)),
                ("cotizacion", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="configuracion_modalidades_pago", to="cotizaciones.cotizacion", verbose_name="Cotización")),
            ],
            options={"verbose_name": "Modalidad de pago de cotización", "verbose_name_plural": "Modalidades de pago de cotizaciones", "ordering": ["-fecha_actualizacion"]},
        )
    ]
