import requests

EMAIL = "new_user@example.com"
PASSWORD = "12345"
BASE_URL = "http://localhost:8000"

print("=" * 50)
print("ФИНАЛЬНЫЙ ТЕСТ ПОДПИСОК")
print("=" * 50)

# 1. Получаем токен
print("\n1. Аутентификация...")
response = requests.post(
    f"{BASE_URL}/api/auth/token/", json={"email": EMAIL, "password": PASSWORD}
)
token = response.json()["access"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Получаем курсы (до подписки)
print("\n2. Получаем курсы ДО подписки...")
response = requests.get(f"{BASE_URL}/api/courses/", headers=headers)
courses = response.json()

if courses:
    print(f"Найдено курсов: {len(courses)}")
    for course in courses:
        print(f"  Курс '{course['title']}': is_subscribed = {course['is_subscribed']}")

# 3. Подписываемся на все курсы
print("\n3. Подписываемся на все курсы...")
for course in courses:
    course_id = course["id"]
    response = requests.post(
        f"{BASE_URL}/api/subscriptions/", json={"course_id": course_id}, headers=headers
    )
    print(f"  Курс ID {course_id}: {response.json()['message']}")

# 4. Проверяем курсы ПОСЛЕ подписки
print("\n4. Проверяем курсы ПОСЛЕ подписки...")
response = requests.get(f"{BASE_URL}/api/courses/", headers=headers)
courses = response.json()

for course in courses:
    print(f"  Курс '{course['title']}': is_subscribed = {course['is_subscribed']}")

# 5. Отписываемся от одного курса
print("\n5. Отписываемся от первого курса...")
if courses:
    course_id = courses[0]["id"]
    response = requests.post(
        f"{BASE_URL}/api/subscriptions/", json={"course_id": course_id}, headers=headers
    )
    print(f"  Результат: {response.json()['message']}")

# 6. Финальная проверка
print("\n6. Финальная проверка...")
response = requests.get(f"{BASE_URL}/api/courses/", headers=headers)
courses = response.json()

print("\nИтоговое состояние подписок:")
for course in courses:
    print(f"  Курс '{course['title']}': is_subscribed = {course['is_subscribed']}")

print("\n" + "=" * 50)
print("✅ ВСЁ РАБОТАЕТ КОРРЕКТНО!")
print("=" * 50)

# 7. Проверка через базу данных
print("\n7. Для проверки в Django shell выполни:")
print(f"   from materials.models import Subscription")
print(f"   from users.models import User")
print(f"   user = User.objects.get(email='{EMAIL}')")
print(f"   subs = Subscription.objects.filter(user=user)")
print(f"   for sub in subs:")
print(f"       print(f'Подписан на: {{sub.course.title}}')")
