from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Note",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField("tytuł", max_length=256)),
                ("body", models.TextField("treść")),
                ("created_at", models.DateTimeField("utworzono", auto_now_add=True)),
            ],
            options={"ordering": ["-created_at", "-pk"], "verbose_name": "notatka", "verbose_name_plural": "notatki"},
        ),
    ]
