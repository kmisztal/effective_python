from django.views.generic import DetailView, ListView
from .models import Note

class NoteListView(ListView):
    model = Note
    context_object_name = "notes"
    paginate_by = 5

class NoteDetailView(DetailView):
    model = Note
    context_object_name = "note"
