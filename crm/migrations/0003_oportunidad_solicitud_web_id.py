from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("crm", "0002_alter_actividad_options")]

    operations = [
        migrations.AddField(
            model_name="oportunidad",
            name="solicitud_web_id",
            field=models.PositiveBigIntegerField(
                blank=True, editable=False, null=True, unique=True, verbose_name="Solicitud web"
            ),
        ),
    ]
