from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Course, Lesson, Subscription

User = get_user_model()


class LessonCRUDTestCase(APITestCase):
    """
    Тесты CRUD операций для уроков.
    """

    def setUp(self):
        """
        Настройка тестовых данных.
        """
        # Создаём пользователей
        self.owner = User.objects.create(
            email="owner@example.com",
        )
        self.owner.set_password("testpass123")
        self.owner.save()

        self.other_user = User.objects.create(
            email="other@example.com",
        )
        self.other_user.set_password("testpass123")
        self.other_user.save()

        # Создаём курс
        self.course = Course.objects.create(
            title="Тестовый курс", description="Описание курса", owner=self.owner
        )

        # Создаём урок
        self.lesson = Lesson.objects.create(
            title="Тестовый урок",
            description="Описание урока",
            video_link="https://www.youtube.com/watch?v=test123",
            course=self.course,
            owner=self.owner,
        )

        # URL для уроков
        self.list_url = reverse("lesson-list")  # /api/lessons/
        self.detail_url = reverse("lesson-detail", kwargs={"pk": self.lesson.pk})

    def test_lesson_list_authenticated(self):
        """
        Тест: авторизованный пользователь может видеть список уроков.
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_lesson_list_unauthenticated(self):
        """
        Тест: неавторизованный пользователь не может видеть уроки.
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lesson_create_by_owner(self):
        """
        Тест: владелец может создавать уроки.
        """
        self.client.force_authenticate(user=self.owner)
        data = {
            "title": "Новый урок",
            "description": "Описание нового урока",
            "video_link": "https://www.youtube.com/watch?v=new123",
            "course": self.course.id,
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_lesson_create_invalid_youtube_link(self):
        """
        Тест: нельзя создать урок с не-youtube ссылкой.
        """
        self.client.force_authenticate(user=self.owner)
        data = {
            "title": "Урок с плохой ссылкой",
            "description": "Описание",
            "video_link": "https://vimeo.com/test",  # не YouTube!
            "course": self.course.id,
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("video_link", response.data)

    def test_lesson_update_by_owner(self):
        """
        Тест: владелец может обновлять свой урок.
        """
        self.client.force_authenticate(user=self.owner)
        data = {"title": "Обновлённое название"}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Обновлённое название")

    def test_lesson_update_by_other_user(self):
        """
        Тест: другой пользователь не может обновлять чужой урок.
        """
        self.client.force_authenticate(user=self.other_user)
        data = {"title": "Попытка изменить"}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_lesson_delete_by_owner(self):
        """
        Тест: владелец может удалять свой урок.
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_lesson_delete_by_other_user(self):
        """
        Тест: другой пользователь не может удалять чужой урок.
        """
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Lesson.objects.count(), 1)


class SubscriptionTestCase(APITestCase):
    """
    Тесты функционала подписок.
    """

    def setUp(self):
        """
        Настройка тестовых данных.
        """
        # Создаём пользователя
        self.user = User.objects.create(email="subscriber@example.com")
        self.user.set_password("testpass123")
        self.user.save()

        # Создаём курс
        self.course = Course.objects.create(
            title="Курс для подписки", description="Описание", owner=self.user
        )

        # URL для подписок
        self.subscription_url = reverse("subscription")

    def test_subscribe(self):
        """
        Тест: пользователь может подписаться на курс.
        """
        self.client.force_authenticate(user=self.user)

        # Подписываемся
        response = self.client.post(
            self.subscription_url, {"course_id": self.course.id}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Подписка добавлена")

        # Проверяем, что подписка создалась
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_unsubscribe(self):
        """
        Тест: пользователь может отписаться от курса.
        """
        self.client.force_authenticate(user=self.user)

        # Сначала подписываемся
        Subscription.objects.create(user=self.user, course=self.course)

        # Затем отписываемся
        response = self.client.post(
            self.subscription_url, {"course_id": self.course.id}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка удалена")

        # Проверяем, что подписки нет
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_subscribe_toggle(self):
        """
        Тест: переключение подписки (подписаться → отписаться → подписаться).
        """
        self.client.force_authenticate(user=self.user)

        # Первый раз - подписываемся
        response = self.client.post(
            self.subscription_url, {"course_id": self.course.id}, format="json"
        )
        self.assertEqual(response.data["message"], "Подписка добавлена")

        # Второй раз - отписываемся
        response = self.client.post(
            self.subscription_url, {"course_id": self.course.id}, format="json"
        )
        self.assertEqual(response.data["message"], "Подписка удалена")

        # Третий раз - снова подписываемся
        response = self.client.post(
            self.subscription_url, {"course_id": self.course.id}, format="json"
        )
        self.assertEqual(response.data["message"], "Подписка добавлена")

        # Проверяем конечное состояние
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_subscribe_without_course_id(self):
        """
        Тест: ошибка при попытке подписаться без course_id.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.subscription_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_subscribe_nonexistent_course(self):
        """
        Тест: ошибка при попытке подписаться на несуществующий курс.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.subscription_url,
            {"course_id": 9999},  # несуществующий ID
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
