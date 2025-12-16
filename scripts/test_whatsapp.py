import json
import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
from whastsapp_api import send_mensage

def run():
    r1 = send_mensage("", "Teste vazio")
    print(json.dumps({"case": "invalid_number", "result": r1}, ensure_ascii=False))
    r2 = send_mensage("1199999999", "Teste de envio")
    print(json.dumps({"case": "send_attempt", "result": r2}, ensure_ascii=False))

if __name__ == "__main__":
    run()
