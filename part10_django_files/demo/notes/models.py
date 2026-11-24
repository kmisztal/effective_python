from django.db import models

class Note(models.Model):
    title = models.CharField("tytuł", max_length=256)
    body = models.TextField("treść")
    created_at = models.DateTimeField("utworzono", auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        verbose_name = "notatka"
        verbose_name_plural = "notatki"

    def __str__(self):
        return self.title
