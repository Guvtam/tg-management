from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("soporte", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="ticket",
            name="empresa",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="tickets", to="crm.empresa", verbose_name="Cliente"),
        ),
        migrations.AddField(model_name="ticket", name="solicitud_web_id", field=models.UUIDField(blank=True, editable=False, null=True, unique=True)),
        migrations.AddField(model_name="ticket", name="nombre_reportante", field=models.CharField(blank=True, max_length=120, verbose_name="Nombre del reportante")),
        migrations.AddField(model_name="ticket", name="correo_reportante", field=models.EmailField(blank=True, max_length=254, verbose_name="Correo del reportante")),
    ]
