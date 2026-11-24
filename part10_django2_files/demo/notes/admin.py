from django.contrib import admin
from .models import Note

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "created_at")
    search_fields = ("title", "body", "owner__username")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)
