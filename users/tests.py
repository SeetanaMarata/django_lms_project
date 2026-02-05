from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserAPITestCase(APITestCase):
    """
    Тесты для API пользователей.
    """

    def setUp(self):
        self.user = User.objects.create(email="testuser@example.com")
        self.user.set_password("testpass123")
        self.user.save()

        self.other_user = User.objects.create(email="otheruser@example.com")
        self.other_user.set_password("testpass123")
        self.other_user.save()

    def get_token(self, user):
        """Получить JWT токен для пользователя."""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_user_registration(self):
        """
        Тест регистрации нового пользователя.
        """
        url = reverse("register")
        data = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "first_name": "Новый",
            "last_name": "Пользователь",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)

    def test_user_login(self):
        """
        Тест получения JWT токена.
        """
        url = reverse("token_obtain_pair")
        data = {"email": "testuser@example.com", "password": "testpass123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_profile_me(self):
        """
        Тест получения своего профиля.
        """
        url = reverse("user-me")
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.get_token(self.user)}"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_user_list_authenticated(self):
        """
        Тест списка пользователей (только для авторизованных).
        """
        url = reverse("user-list")
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.get_token(self.user)}"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_list_unauthenticated(self):
        """
        Тест: неавторизованные не могут видеть список пользователей.
        """
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PaymentAPITestCase(APITestCase):
    """
    Тесты для API платежей.
    """

    def setUp(self):
        from materials.models import Course, Lesson
        from users.models import Payment

        self.user = User.objects.create(email="payer@example.com")
        self.user.set_password("testpass123")
        self.user.save()

        # Создаём тестовые данные
        self.course = Course.objects.create(
            title="Платный курс", description="Описание", owner=self.user
        )

        self.lesson = Lesson.objects.create(
            title="Платный урок",
            description="Описание",
            video_link="https://www.youtube.com/watch?v=test",
            course=self.course,
            owner=self.user,
        )

        # Создаём платежи
        self.payment1 = Payment.objects.create(
            user=self.user,
            course=self.course,
            amount=1000.00,
            payment_method="transfer",
        )

        self.payment2 = Payment.objects.create(
            user=self.user, lesson=self.lesson, amount=500.00, payment_method="cash"
        )

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_payment_list_authenticated(self):
        """
        Тест списка платежей для авторизованного пользователя.
        """
        url = reverse("payment-list")
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.get_token(self.user)}"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_payment_filter_by_course(self):
        """
        Тест фильтрации платежей по курсу.
        """
        url = reverse("payment-list") + f"?course={self.course.id}"
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.get_token(self.user)}"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Должен быть хотя бы один платеж за курс
        self.assertGreater(len(response.data), 0)

    def test_payment_filter_by_payment_method(self):
        """
        Тест фильтрации платежей по способу оплаты.
        """
        url = reverse("payment-list") + "?payment_method=transfer"
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.get_token(self.user)}"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
