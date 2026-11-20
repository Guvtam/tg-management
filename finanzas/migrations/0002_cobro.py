# Modelo inicial de cobros con enlaces individuales (sin pasarela).
import django.db.models.deletion
import finanzas.cobros
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("finanzas", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Cobro",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("token", models.CharField(default=finanzas.cobros.generar_token, editable=False, max_length=64, unique=True)),
                ("estado", models.CharField(choices=[
                    ("pendiente", "Pendiente"),
                    ("en_proceso", "En proceso"),
                    ("pagado", "Pagado"),
                    ("vencido", "Vencido"),
                    ("anulado", "Anulado"),
                ], default="pendiente", max_length=20)),
                ("referencia_proveedor", models.CharField(blank=True, db_index=True, max_length=150)),
                ("proveedor", models.CharField(blank=True, max_length=40)),
                ("fecha_confirmacion", models.DateTimeField(blank=True, null=True)),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                ("actualizado_en", models.DateTimeField(auto_now=True)),
                ("ingreso", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="cobro", to="finanzas.ingreso")),
            ],
            options={"verbose_name": "Cobro", "verbose_name_plural": "Cobros", "ordering": ["-creado_en"]},
        ),
    ]
