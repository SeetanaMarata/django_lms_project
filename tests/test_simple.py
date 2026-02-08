import json

import requests

EMAIL = "new_user@example.com"
PASSWORD = "12345"
BASE_URL = "http://localhost:8000"

print("1. Получаем токен...")
response = requests.post(
    f"{BASE_URL}/api/auth/token/", json={"email": EMAIL, "password": PASSWORD}
)
token = response.json()["access"]
headers = {"Authorization": f"Bearer {token}"}

print("\n2. Проверяем URL подписок...")
# Попробуем разные варианты URL
urls_to_test = [
    "/api/subscriptions/",
    "/api/materials/subscriptions/",
    "/subscriptions/",
]

for url in urls_to_test:
    full_url = BASE_URL + url
    print(f"\nПробуем: {full_url}")
    response = requests.get(full_url, headers=headers)
    print(f"Статус: {response.status_code}")
    if response.status_code != 404:
        print(f"Ответ: {response.text[:100]}...")

print("\n3. Проверяем POST запрос...")
# Используем правильный URL (после того как найдём)
test_url = BASE_URL + "/api/subscriptions/"
data = {"course_id": 2}

print(f"URL: {test_url}")
print(f"Данные: {data}")
print(f"Заголовки: {headers}")

response = requests.post(test_url, json=data, headers=headers)
print(f"\nСтатус: {response.status_code}")
print(f"Ответ: {response.text}")
