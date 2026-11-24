from django.db import models
from django.conf import settings

class Note(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes", verbose_name="właściciel")
    title = models.CharField("tytuł", max_length=256)
    body = models.TextField("treść")
    created_at = models.DateTimeField("utworzono", auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        verbose_name = "notatka"
        verbose_name_plural = "notatki"

    def __str__(self):
        return self.title
