from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from .forms import ContactForm, NoteForm
from .models import Note

class NotesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.alice = get_user_model().objects.create_user("alice", password="test-password")
        cls.bob = get_user_model().objects.create_user("bob", password="test-password")
        cls.note = Note.objects.create(owner=cls.alice, title="Notatka Alice", body="Treść")
        cls.other = Note.objects.create(owner=cls.bob, title="Sekret Boba", body="Inna treść")

    def setUp(self):
        self.client.force_login(self.alice)

    def test_login_required(self):
        self.client.logout()
        for url in ["/notes/", "/notes/new/", f"/notes/{self.note.pk}/", "/notes/contact/"]:
            self.assertEqual(self.client.get(url).status_code, 302)

    def test_own_list_only(self):
        response = self.client.get("/notes/")
        self.assertContains(response, "Notatka Alice")
        self.assertNotContains(response, "Sekret Boba")

    def test_other_object_get_denied(self):
        for suffix in ["", "edit/", "delete/"]:
            self.assertEqual(self.client.get(f"/notes/{self.other.pk}/{suffix}").status_code, 404)

    def test_other_object_post_denied(self):
        for suffix in ["edit/", "delete/"]:
            self.assertEqual(self.client.post(f"/notes/{self.other.pk}/{suffix}", {"title": "Atak", "body": "X"}).status_code, 404)
        self.other.refresh_from_db()
        self.assertEqual(self.other.title, "Sekret Boba")

    def test_owner_is_server_assigned(self):
        response = self.client.post("/notes/new/", {"title": "Nowa", "body": "Treść", "owner": self.bob.pk})
        self.assertRedirects(response, "/notes/")
        self.assertEqual(Note.objects.get(title="Nowa").owner, self.alice)

    def test_invalid_create_keeps_errors(self):
        before = Note.objects.count()
        response = self.client.post("/notes/new/", {"title": "ab", "body": "Treść"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "co najmniej 3")
        self.assertEqual(Note.objects.count(), before)

    def test_empty_post_is_bound(self):
        response = self.client.post("/notes/new/", {})
        self.assertTrue(response.context["form"].is_bound)
        self.assertTrue(response.context["form"].errors)

    def test_update(self):
        response = self.client.post(f"/notes/{self.note.pk}/edit/", {"title": "Zmieniona", "body": "Nowa treść", "owner": self.bob.pk})
        self.assertRedirects(response, "/notes/")
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "Zmieniona")
        self.assertEqual(self.note.owner, self.alice)

    def test_delete_get_does_not_delete(self):
        self.assertEqual(self.client.get(f"/notes/{self.note.pk}/delete/").status_code, 200)
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())

    def test_delete_post(self):
        self.assertRedirects(self.client.post(f"/notes/{self.note.pk}/delete/"), "/notes/")
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.alice)
        data = {"title": "CSRF demo", "body": "Treść"}
        self.assertEqual(client.post("/notes/new/", data).status_code, 403)
        client.get("/notes/new/")
        token = client.cookies["csrftoken"].value
        self.assertRedirects(client.post("/notes/new/", data, HTTP_X_CSRFTOKEN=token), "/notes/")

    def test_autoescape(self):
        self.note.body = "<script>alert(1)</script>"
        self.note.save()
        response = self.client.get(reverse("notes:note-detail", args=[self.note.pk]))
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")

    def test_contact_validation_and_prg(self):
        self.assertEqual(self.client.get("/notes/contact/").status_code, 200)
        invalid = self.client.post("/notes/contact/", {"subject": "Hej", "message": "X", "sender": "bad"})
        self.assertTrue(invalid.context["form"].errors)
        valid = self.client.post("/notes/contact/", {"subject": "Hej", "message": "X", "sender": "a@example.invalid"})
        self.assertRedirects(valid, "/notes/contact/thanks/")

    def test_explicit_form_fields(self):
        self.assertEqual(list(NoteForm().fields), ["title", "body"])
        self.assertFalse(ContactForm(data={}).is_valid())

    def test_login_logout(self):
        self.client.logout()
        self.assertEqual(self.client.get("/accounts/login/").status_code, 200)
        self.assertRedirects(self.client.post("/accounts/login/", {"username": "alice", "password": "test-password"}), "/notes/")
        self.assertEqual(self.client.get("/accounts/logout/").status_code, 405)
        self.assertRedirects(self.client.post("/accounts/logout/"), "/accounts/login/")

    def test_about(self):
        self.assertContains(self.client.get("/notes/about/"), "O aplikacji")
