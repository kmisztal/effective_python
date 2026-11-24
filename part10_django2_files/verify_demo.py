"""Sprawdź projekt na kopii i bazie tymczasowej."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

source = Path(__file__).resolve().parent / "demo"
with TemporaryDirectory(prefix="django_lecture_") as temporary:
    target = Path(temporary) / "demo"
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("db.sqlite3", "__pycache__"))
    environment = {**os.environ, "PYTHONIOENCODING": "utf-8", "DJANGO_DEMO_DB": str(target / "db.sqlite3")}
    for arguments in [["check"], ["makemigrations", "--check", "--dry-run"], ["migrate", "--noinput"], ["test", "notes", "--noinput"]]:
        completed = subprocess.run([sys.executable, "manage.py", *arguments], cwd=target, env=environment, capture_output=True, text=True, encoding="utf-8", timeout=90)
        if completed.returncode:
            print(completed.stdout, completed.stderr)
            raise SystemExit(completed.returncode)
        print("OK:", " ".join(arguments))
        if arguments[0] == "test":
            print(completed.stderr.strip())
