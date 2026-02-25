import os
import sys

import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_lms_project.settings")
django.setup()

import stripe
from django.conf import settings

print("🔑 Проверка ключей Stripe...")
print(f"Publishable key: {settings.STRIPE_PUBLISHABLE_KEY[:20]}...")
print(f"Secret key: {settings.STRIPE_SECRET_KEY[:20]}...")

# Проверяем, что ключи не None
if not settings.STRIPE_SECRET_KEY:
    print("❌ STRIPE_SECRET_KEY не найден в настройках")
    sys.exit(1)

# Инициализируем Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Проверяем соединение с Stripe API
try:
    # Простой запрос для проверки
    balance = stripe.Balance.retrieve()
    print("✅ Подключение к Stripe успешно!")
    print(
        f"💰 Баланс доступен: {balance.available[0].amount if balance.available else 0} копеек"
    )
except stripe.error.AuthenticationError:
    print("❌ Ошибка аутентификации. Проверь ключи.")
    print("🔍 Убедись, что в ключах нет пробелов")
except Exception as e:
    print(f"❌ Ошибка: {type(e).__name__}: {e}")
