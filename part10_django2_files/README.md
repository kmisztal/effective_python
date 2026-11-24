# Django — część 2

Osobny projekt demonstracyjny, kontynuujący model notatki z części 1. Python 3.10, Django 5.2 LTS.
Korzystaj z nowej bazy: nie kopiuj db.sqlite3 z części 1. Dodanie wymaganego właściciela istniejącym danym wymaga osobnego planu migracji.

```text
python -m pip install -r part10_django2_files/requirements.txt
cd part10_django2_files/demo
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8000
```

Otwórz /accounts/login/, zaloguj się utworzonym kontem i dodaj notatkę przez /notes/new/. W panelu /admin/ możesz utworzyć drugie zwykłe konto do demonstracji izolacji. Publiczne widoki filtrują notatki według zalogowanego właściciela; admin zachowuje swoje standardowe uprawnienia i nie ma tego filtrowania.

Kontakt jest demonstracją walidacji, bez wysyłania e-maila i bez zapisu danych. Własne formularze obejmują tworzenie, edycję i potwierdzanie usunięcia notatki.

Kontrola na tymczasowej bazie z katalogu repozytorium:

```text
python part10_django2_files/verify_demo.py
```

Konfiguracja służy lokalnemu wykładowi. Rozszerzenie projektu nie zmienia demonstracji z pierwszej części.
