from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = "notes"
urlpatterns = [
    path("", views.NoteListView.as_view(), name="note-list"),
    path("new/", views.NoteCreateView.as_view(), name="note-create"),
    path("<int:pk>/", views.NoteDetailView.as_view(), name="note-detail"),
    path("<int:pk>/edit/", views.NoteUpdateView.as_view(), name="note-update"),
    path("<int:pk>/delete/", views.NoteDeleteView.as_view(), name="note-delete"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("contact/thanks/", login_required(TemplateView.as_view(
        template_name="notes/contact_thanks.html")), name="contact-thanks"),
]
