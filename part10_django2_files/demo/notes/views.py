from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from .forms import ContactForm, NoteForm
from .models import Note

class OwnedNotesMixin(LoginRequiredMixin):
    model = Note
    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)

class NoteListView(OwnedNotesMixin, ListView):
    context_object_name = "notes"
    paginate_by = 5

class NoteDetailView(OwnedNotesMixin, DetailView):
    context_object_name = "note"

class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    form_class = NoteForm
    success_url = reverse_lazy("notes:note-list")
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class NoteUpdateView(OwnedNotesMixin, UpdateView):
    form_class = NoteForm
    success_url = reverse_lazy("notes:note-list")

class NoteDeleteView(OwnedNotesMixin, DeleteView):
    success_url = reverse_lazy("notes:note-list")

def about(request):
    return render(request, "notes/about.html", {"now": timezone.now()})

@login_required
def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Demo walidacji: bez wysyłki e-mail i bez zapisu danych.
            return redirect("notes:contact-thanks")
    else:
        form = ContactForm()
    return render(request, "notes/contact.html", {"form": form})
