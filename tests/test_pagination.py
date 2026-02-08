import time

import requests

EMAIL = "new_user@example.com"
PASSWORD = "12345"
BASE_URL = "http://localhost:8000"

print("=" * 50)
print("ТЕСТ ПАГИНАЦИИ")
print("=" * 50)

# 1. Получаем токен
print("\n1. Аутентификация...")
response = requests.post(
    f"{BASE_URL}/api/auth/token/", json={"email": EMAIL, "password": PASSWORD}
)
token = response.json()["access"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Создадим больше курсов для теста пагинации
print("\n2. Создаём тестовые курсы...")
# Пропусти этот шаг, если у тебя уже много курсов
# Если мало - создай через Django shell

# 3. Тестируем пагинацию курсов
print("\n3. Тестируем пагинацию курсов...")

test_urls = [
    "/api/courses/",
    "/api/courses/?page=1",
    "/api/courses/?page_size=2",
    "/api/courses/?page=1&page_size=3",
]

for url in test_urls:
    print(f"\nЗапрос: {url}")
    response = requests.get(BASE_URL + url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(f"Статус: {response.status_code}")

        # Проверяем структуру ответа с пагинацией
        if "results" in data:
            print(f"✅ Пагинация работает!")
            print(f"   Всего элементов: {data.get('count', '?')}")
            print(f"   Элементов на странице: {len(data['results'])}")
            print(f"   Следующая страница: {data.get('next', 'нет')}")
            print(f"   Предыдущая страница: {data.get('previous', 'нет')}")
        else:
            print(f"ℹ️  Ответ без пагинации: {len(data)} элементов")
    else:
        print(f"❌ Ошибка: {response.status_code}")
        print(f"   Ответ: {response.text[:100]}")

# 4. Тестируем пагинацию уроков
print("\n4. Тестируем пагинацию уроков...")

# Сначала создадим несколько уроков если их мало
print("   Создайте несколько уроков через админку или API если их меньше 5")

# Тестируем
lesson_urls = ["/api/lessons/", "/api/lessons/?page_size=2"]

for url in lesson_urls:
    print(f"\nЗапрос: {url}")
    response = requests.get(BASE_URL + url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(f"Статус: {response.status_code}")

        if "results" in data:
            print(f"✅ Пагинация работает для уроков!")
            print(f"   Всего уроков: {data.get('count', '?')}")
            print(f"   Уроков на странице: {len(data['results'])}")
        else:
            print(f"ℹ️  Ответ без пагинации: {len(data)} уроков")
    else:
        print(f"❌ Ошибка: {response.status_code}")

print("\n" + "=" * 50)
print("ТЕСТ ЗАВЕРШЁН")
print("=" * 50)
