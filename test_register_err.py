import requests
import json

URL = "http://127.0.0.1:8001/auth/register"
payload = {
    "username": "tester_" + str(hash("user")),
    "password": "Password123!",
    "email": "test@example.com",
    "full_name": "Test User",
    "phone": "123456789",
    "birth_date": "1990-01-01",
    "currency": "COP",
    "role": "admin"
}

print(f"Enviando POST para {URL}...")
try:
    response = requests.post(URL, json=payload)
    print(f"Status Code: {response.status_code}")
    print("Response Body:", response.text)
except Exception as e:
    print(f"Erro ao enviar requisição: {e}")
