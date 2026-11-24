from django import forms
from .models import Note

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["title", "body"]

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if len(title) < 3:
            raise forms.ValidationError("Tytuł musi mieć co najmniej 3 znaki.")
        return title

class ContactForm(forms.Form):
    subject = forms.CharField(label="Temat", max_length=100)
    message = forms.CharField(label="Wiadomość", widget=forms.Textarea)
    sender = forms.EmailField(label="E-mail")
    cc_myself = forms.BooleanField(label="Kopia dla mnie", required=False)
