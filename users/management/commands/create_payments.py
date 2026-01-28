import random
from datetime import datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand

from materials.models import Course, Lesson
from users.models import Payment, User


class Command(BaseCommand):
    help = "Создает тестовые платежи для базы данных"

    def handle(self, *args, **options):
        # Получаем или создаем тестовые данные
        user, _ = User.objects.get_or_create(
            email="test_user@example.com",
            defaults={"first_name": "Test", "last_name": "User"},
        )

        # Получаем или создаем курс и урок
        course, _ = Course.objects.get_or_create(
            title="Тестовый курс Django",
            defaults={"description": "Курс по Django для начинающих"},
        )

        lesson, _ = Lesson.objects.get_or_create(
            title="Тестовый урок",
            course=course,
            defaults={
                "description": "Введение в Django",
                "video_link": "https://youtube.com/test",
            },
        )

        # Создаем платежи
        payment_methods = ["cash", "transfer"]

        payments_data = [
            {
                "user": user,
                "course": course,
                "lesson": None,
                "amount": Decimal("10000.00"),
                "payment_method": "transfer",
            },
            {
                "user": user,
                "course": None,
                "lesson": lesson,
                "amount": Decimal("1500.00"),
                "payment_method": "cash",
            },
            {
                "user": user,
                "course": course,
                "lesson": None,
                "amount": Decimal("12000.00"),
                "payment_method": "transfer",
            },
        ]

        created_count = 0
        for i, data in enumerate(payments_data):
            # Разные даты для каждого платежа
            payment_date = datetime.now() - timedelta(days=i * 10)

            payment, created = Payment.objects.get_or_create(
                user=data["user"],
                course=data["course"],
                lesson=data["lesson"],
                defaults={
                    "amount": data["amount"],
                    "payment_method": data["payment_method"],
                    "payment_date": payment_date,
                },
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Создан платеж: {payment.user.email} - {payment.amount} руб."
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(f"Успешно создано {created_count} платежей")
        )
