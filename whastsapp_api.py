import os
from django.conf import settings


def send_mensage(number: str, text: str):
    import requests
    base_url = getattr(settings, 'EVOLUTION_API_URL', 'http://localhost:8082')
    api_key = getattr(settings, 'EVOLUTION_API_KEY', os.getenv('AUTHENTICATION_API_KEY', ''))
    url = base_url.rstrip('/') + "/message/sendText/main_phone"
    DEFAULT_COUNTRY_CODE = "55"
    payload = {
        "number": DEFAULT_COUNTRY_CODE + number,
        "textMessage": {
            "text": text
        },
    }
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }

    if not api_key:
        print('missing apikey')
        return None
    response = requests.post(url, json=payload, headers=headers)
    print(f'number: {number}')
    print(f'text: {text}')
    print(response.status_code)
    print(response.text)
