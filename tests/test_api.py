import requests

# ДАННЫЕ ДЛЯ АВТОРИЗАЦИИ
EMAIL = "new_user@example.com"
PASSWORD = "12345"
BASE_URL = "http://localhost:8000"

print("=" * 50)
print("ТЕСТИРОВАНИЕ API ПОДПИСОК")
print("=" * 50)

# 1. ПОЛУЧЕНИЕ ТОКЕНА
print("\n1. Получаем JWT токен...")
try:
    response = requests.post(
        f"{BASE_URL}/api/auth/token/",
        json={"email": EMAIL, "password": PASSWORD},
        timeout=10,
    )

    if response.status_code != 200:
        print(f"❌ Ошибка авторизации!")
        print(f"Код: {response.status_code}")
        print(f"Ответ: {response.text}")
        exit()

    token_data = response.json()
    access_token = token_data["access"]
    print(f"✅ Токен получен успешно")

except requests.exceptions.ConnectionError:
    print("❌ Не могу подключиться к серверу!")
    print(f"Убедись, что сервер запущен: python manage.py runserver")
    exit()

# Заголовок с токеном для всех следующих запросов
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}

# 2. ПРОВЕРКА КУРСОВ
print("\n2. Получаем список курсов...")
try:
    response = requests.get(f"{BASE_URL}/api/courses/", headers=headers, timeout=10)

    if response.status_code != 200:
        print(f"❌ Ошибка получения курсов: {response.status_code}")
        print(response.text)
        exit()

    courses = response.json()

    if not courses:
        print("ℹ️  Нет доступных курсов.")
        print("Создайте курс через админку или API")
        exit()

    print(f"✅ Найдено курсов: {len(courses)}")

    # Показываем первый курс
    first_course = courses[0]
    print(f"\nПервый курс:")
    print(f"  ID: {first_course['id']}")
    print(f"  Название: {first_course['title']}")
    print(f"  Подписка активна: {first_course.get('is_subscribed', False)}")

    course_id = first_course["id"]

except Exception as e:
    print(f"❌ Ошибка: {e}")
    exit()

# 3. ПОДПИСКА НА КУРС
print(f"\n3. Подписываемся на курс ID={course_id}...")
try:
    response = requests.post(
        f"{BASE_URL}/api/subscriptions/",
        json={"course_id": course_id},
        headers=headers,
        timeout=10,
    )

    result = response.json()
    print(f"✅ Результат: {result['message']}")

except Exception as e:
    print(f"❌ Ошибка подписки: {e}")
    exit()

# 4. ПРОВЕРКА ИЗМЕНЕНИЙ
print("\n4. Проверяем изменения...")
try:
    response = requests.get(f"{BASE_URL}/api/courses/", headers=headers, timeout=10)
    courses = response.json()

    if courses:
        course = courses[0]
        print(f"✅ Теперь подписка активна: {course['is_subscribed']}")

    # Дополнительно: проверяем саму подписку
    print("\n5. Проверяем список подписок через базу данных...")
    print("Запусти в Django shell:")
    print(f"  from materials.models import Subscription")
    print(f"  from users.models import User")
    print(f"  user = User.objects.get(email='{EMAIL}')")
    print(f"  subscriptions = Subscription.objects.filter(user=user)")
    print(f"  print(f'У пользователя {EMAIL} подписок: {{subscriptions.count()}}')")

except Exception as e:
    print(f"❌ Ошибка проверки: {e}")

print("\n" + "=" * 50)
print("ТЕСТ ЗАВЕРШЁН")
print("=" * 50)

# 5. ДОПОЛНИТЕЛЬНО: ПРОВЕРКА РАБОТЫ ПОДПИСКИ (ВКЛ/ВЫКЛ)
print("\n6. Тестируем переключение подписки...")
print("Отправьте ещё раз POST запрос на /api/subscriptions/")
print(f"с course_id={course_id} чтобы ОТПИСАТЬСЯ")
print("Затем проверьте, что is_subscribed станет False")
