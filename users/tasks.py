from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from users.models import User


@shared_task
def deactivate_inactive_users():
    """
    Блокирует пользователей, которые не заходили более 30 дней.
    """
    month_ago = timezone.now() - timedelta(days=30)

    # Ищем пользователей, которые:
    # 1. Не заходили больше месяца
    # 2. Ещё активны
    inactive_users = User.objects.filter(last_login__lt=month_ago, is_active=True)

    count = inactive_users.count()
    inactive_users.update(is_active=False)

    print(f"🚫 Заблокировано пользователей: {count}")
    return f"Deactivated {count} users"
