import json
import os
import sys
import django
from django.conf import settings

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Configure Django settings if not already configured
if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

from whastsapp_api import send_mensage

def run():
    print("Running send_mensage tests...")
    # Test 1: Invalid number (should return error dict, not None)
    r1 = send_mensage("", "Teste vazio")
    print("Test 1 Result:", json.dumps(r1, ensure_ascii=False))

    # Test 2: Valid number (should return success or error dict, not None)
    r2 = send_mensage("1199999999", "Teste de envio")
    print("Test 2 Result:", json.dumps(r2, ensure_ascii=False))

if __name__ == "__main__":
    run()
