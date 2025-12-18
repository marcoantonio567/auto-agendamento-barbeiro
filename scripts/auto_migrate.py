import os
import sys
import django
from django.conf import settings
from django.core.management import call_command

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if not settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    django.setup()

def main():
    print("Executando makemigrations...")
    call_command("makemigrations")
    print("Executando migrate...")
    call_command("migrate", interactive=False)
    print("Migrações concluídas com sucesso.")

if __name__ == "__main__":
    main()
