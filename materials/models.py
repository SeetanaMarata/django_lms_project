from django.db import models

from users.models import User

from .validators import validate_youtube_only


class Course(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    preview = models.ImageField(
        upload_to="courses/", null=True, blank=True, verbose_name="Превью"
    )
    description = models.TextField(verbose_name="Описание")

    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,  # если пользователь удален, курс остается
        null=True,
        blank=True,
        verbose_name="Владелец",
        related_name="courses",  # user.courses - все курсы пользователя
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    preview = models.ImageField(
        upload_to="lessons/", null=True, blank=True, verbose_name="Превью"
    )
    video_link = models.URLField(
        verbose_name="Ссылка на видео",
        validators=[validate_youtube_only],  # добавь валидатор здесь
    )
    course = models.ForeignKey(
        "Course", on_delete=models.CASCADE, related_name="lessons", verbose_name="Курс"
    )
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Владелец",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["created_at"]


class Subscription(models.Model):
    """Модель подписки пользователя на курс"""

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Пользователь",
    )
    course = models.ForeignKey(
        "Course",
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Курс",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подписки")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        # Уникальная пара пользователь-курс
        unique_together = ["user", "course"]

    def __str__(self):
        return f"{self.user.email} подписан на {self.course.title}"
