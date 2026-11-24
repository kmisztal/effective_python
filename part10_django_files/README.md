# Django — demonstracja do pierwszego wykładu

Środowisko: Python 3.10, Django 5.2 LTS. Instalacja z katalogu repozytorium:

```text
python -m pip install -r part10_django_files/requirements.txt
cd part10_django_files/demo
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8000
```

Adresy: http://127.0.0.1:8000/notes/ oraz http://127.0.0.1:8000/admin/.
Utwórz notatki w panelu administratora. To lokalna aplikacja dydaktyczna z publiczną listą notatek, bez podziału na właścicieli. Nie wpisuj danych prywatnych. Ustawienia demonstracyjne nie są konfiguracją produkcyjną.

Testy bez zmiany roboczej bazy (z katalogu repozytorium):

```text
python part10_django_files/verify_demo.py
```

Weryfikator kopiuje projekt do katalogu tymczasowego, wykonuje migracje, system checks i testy. Nie tworzy kont w bazie demonstracyjnej.
