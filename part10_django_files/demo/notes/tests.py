from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Note

class NoteViewsTests(TestCase):
    def test_empty_list(self):
        response = self.client.get(reverse("notes:note-list"))
        self.assertContains(response, "Nie ma jeszcze notatek.")
        self.assertTemplateUsed(response, "notes/note_list.html")

    def test_list_detail_and_escape(self):
        note = Note.objects.create(title="Zażółć", body="<script>alert(1)</script>")
        self.assertContains(self.client.get(reverse("notes:note-list")), note.title)
        response = self.client.get(reverse("notes:note-detail", args=[note.pk]))
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertTemplateUsed(response, "notes/note_detail.html")

    def test_missing_and_invalid_detail(self):
        self.assertEqual(self.client.get("/notes/999999/").status_code, 404)
        self.assertEqual(self.client.get("/notes/abc/").status_code, 404)

    def test_pagination(self):
        for number in range(6):
            Note.objects.create(title=f"Notatka {number}", body="Treść")
        first = self.client.get(reverse("notes:note-list"))
        second = self.client.get(reverse("notes:note-list") + "?page=2")
        self.assertEqual(len(first.context["notes"]), 5)
        self.assertEqual(len(second.context["notes"]), 1)
        self.assertEqual(self.client.get("/notes/?page=99").status_code, 404)

    def test_admin_requires_login(self):
        response = self.client.get(reverse("admin:notes_note_changelist"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_admin_form_validation(self):
        from django.forms import modelform_factory
        form_class = modelform_factory(Note, fields=["title", "body"])
        self.assertFalse(form_class(data={"title": "", "body": "Treść"}).is_valid())
        self.assertFalse(form_class(data={"title": "x" * 257, "body": "Treść"}).is_valid())

    def test_admin_logged_in(self):
        user = get_user_model().objects.create_superuser("teacher", "teacher@example.invalid", "demo-test-password")
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse("admin:notes_note_add")).status_code, 200)

    def test_root_redirect(self):
        self.assertRedirects(self.client.get("/"), reverse("notes:note-list"))
