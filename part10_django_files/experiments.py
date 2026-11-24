"""Sześć eksperymentów Django na bazie SQLite w pamięci, bez danych projektu."""
import argparse
import django
from django.conf import settings

settings.configure(
    SECRET_KEY="public-experiment-only", INSTALLED_APPS=[],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField", USE_TZ=True,
)
django.setup()
from django.db import connection, models, transaction
from django.db.models import F
from django.forms import modelform_factory
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.test.utils import CaptureQueriesContext

class Author(models.Model):
    name = models.CharField(max_length=100)
    class Meta:
        app_label = "experiments"

class Entry(models.Model):
    owner = models.ForeignKey(Author, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    views = models.PositiveIntegerField(default=0)
    class Meta:
        app_label = "experiments"


def setup():
    with connection.schema_editor() as editor:
        editor.create_model(Author)
        editor.create_model(Entry)
    alice = Author.objects.create(name="Alice")
    bob = Author.objects.create(name="Bob")
    for number in range(3):
        Entry.objects.create(owner=alice, title=f"Notatka {number}")
    return alice, bob


def part1(alice, bob):
    with CaptureQueriesContext(connection) as queries:
        plain = [entry.owner.name for entry in Entry.objects.order_by("pk")]
    plain_count = len(queries)
    with CaptureQueriesContext(connection) as queries:
        joined = [entry.owner.name for entry in Entry.objects.select_related("owner").order_by("pk")]
    assert plain == joined == ["Alice"] * 3
    assert plain_count == 4 and len(queries) == 1
    print("N+1 dla 3 notatek:", plain_count, "zapytań; select_related:", len(queries))

    with CaptureQueriesContext(connection) as queries:
        queryset = Entry.objects.filter(owner=alice)
    assert len(queries) == 0
    with CaptureQueriesContext(connection) as queries:
        assert queryset.exists()
    assert len(queries) == 1
    with CaptureQueriesContext(connection) as queries:
        assert queryset.count() == 3
    assert len(queries) == 1
    with CaptureQueriesContext(connection) as queries:
        first = list(queryset)
    assert len(queries) == 1
    with CaptureQueriesContext(connection) as queries:
        second = list(queryset)
        assert queryset.count() == 3 and queryset.exists()
    assert len(queries) == 0 and first == second
    print("QuerySet: filter=0, exists=1, count=1, pierwsza iteracja=1, ponowne użycie cache=0 zapytań")

    form_class = modelform_factory(Entry, fields=["title"])
    form = form_class(data={"title": ""})
    assert not form.is_valid()
    direct = Entry.objects.create(owner=alice, title="")
    assert Entry.objects.get(pk=direct.pk).title == ""
    from django.core.exceptions import ValidationError
    try:
        direct.full_clean()
    except ValidationError:
        pass
    else:
        raise AssertionError("Model powinien odrzucić pusty tytuł")
    print("Walidacja: ModelForm odrzuca pusty tytuł; objects.create zapisuje ''; full_clean zgłasza ValidationError")
    print("blank=False nie jest ograniczeniem CHECK w bazie; NOT NULL nie zakazuje pustego napisu")


def part2(alice, bob):
    secret = Entry.objects.create(owner=alice, title="Prywatna Alice")
    # Antywzorzec tylko w izolowanym eksperymencie, nie w URL-ach aplikacji.
    unsafe_result = Entry.objects.get(pk=secret.pk)
    assert unsafe_result.owner_id != bob.pk
    try:
        get_object_or_404(Entry.objects.filter(owner=bob), pk=secret.pk)
    except Http404:
        pass
    else:
        raise AssertionError("Cudza notatka nie może być dostępna")
    print("Zmiana ID: nieograniczone get(pk) ujawnia cudzą notatkę; QuerySet właściciela daje Http404")

    counter = Entry.objects.create(owner=alice, title="Licznik")
    request_a = Entry.objects.get(pk=counter.pk)
    request_b = Entry.objects.get(pk=counter.pk)
    request_a.views += 1
    request_a.save(update_fields=["views"])
    request_b.views += 1
    request_b.save(update_fields=["views"])
    counter.refresh_from_db()
    assert counter.views == 1
    print("Wymuszony przeplot odczyt-odczyt-zapis-zapis: dwa zwiększenia, wynik", counter.views)
    Entry.objects.filter(pk=counter.pk).update(views=0)
    for _ in range(2):
        Entry.objects.filter(pk=counter.pk).update(views=F("views") + 1)
    counter.refresh_from_db()
    assert counter.views == 2
    print("Dwie aktualizacje F(views)+1: wynik", counter.views)

    before = Entry.objects.count()
    try:
        Entry.objects.create(owner=alice, title="Bez transakcji")
        raise RuntimeError("Błąd przed drugim zapisem")
    except RuntimeError:
        pass
    assert Entry.objects.count() == before + 1
    before_atomic = Entry.objects.count()
    try:
        with transaction.atomic():
            Entry.objects.create(owner=alice, title="Z transakcją")
            raise RuntimeError("Błąd przed drugim zapisem")
    except RuntimeError:
        pass
    assert Entry.objects.count() == before_atomic
    print("Błąd między zapisami: bez atomic zostaje pierwszy rekord; z atomic zapis wycofany")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--part", type=int, choices=[1, 2], required=True)
    args = parser.parse_args()
    actors = setup()
    (part1 if args.part == 1 else part2)(*actors)
