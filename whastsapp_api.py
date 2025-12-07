import requests
import getenv


def send_mensage(number: str, text: str):
    url = "http://localhost:8081/message/sendText/bacalhau"
    DEFAULT_COUNTRY_CODE = "55"
    payload = {
        "number": DEFAULT_COUNTRY_CODE + number,
        "textMessage": {
            "text": text
        },
    }
    headers = {
        "apikey": getenv("AUTHENTICATION_API_KEY"),
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)
