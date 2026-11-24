from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ("notes", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [migrations.AddField(
        model_name="note", name="owner",
        field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
            related_name="notes", to=settings.AUTH_USER_MODEL, verbose_name="właściciel"),
    )]
