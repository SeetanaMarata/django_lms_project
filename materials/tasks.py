from celery import shared_task


@shared_task
def test_task():
    print("✅ Celery работает!")
    return "OK"


from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_course_update_email(course_title, user_email):
    subject = f"Курс обновлён: {course_title}"
    message = f'Курс "{course_title}" был обновлён. Заходи и смотри!'
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )
