from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, viewsets

from users.permissions import IsModerator, IsOwner

from .models import Course, Lesson
from .paginators import MaterialsPagination
from .serializers import CourseSerializer, LessonSerializer

from django.utils import timezone
from datetime import timedelta
from .models import Subscription
from .tasks import send_course_update_email


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с курсами.

    Доступные действия:
    - list: Получить список курсов (с пагинацией)
    - retrieve: Получить детальную информацию о курсе
    - create: Создать новый курс (только для авторизованных пользователей)
    - update: Обновить курс (только владелец или модератор)
    - partial_update: Частично обновить курс
    - destroy: Удалить курс (только владелец)

    Поля в сериализаторе:
    - lessons_count: количество уроков в курсе (автоматически)
    - lessons: список уроков курса
    - is_subscribed: подписан ли текущий пользователь на курс
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MaterialsPagination

    def get_queryset(self):
        """
        Возвращаем queryset в зависимости от прав пользователя.
        """
        queryset = super().get_queryset()

        # Если пользователь модератор - видит все курсы
        if self.request.user.groups.filter(name="moderators").exists():
            return queryset

        # Иначе видит только свои курсы
        return queryset.filter(owner=self.request.user)

    def get_permissions(self):
        """
        Переопределяем права в зависимости от действия (action).
        """
        if self.action == "create":
            # Создавать курсы могут только не-модераторы
            self.permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        elif self.action == "destroy":
            # Удалять курсы могут только владельцы
            self.permission_classes = [permissions.IsAuthenticated, IsOwner]
        elif self.action in ["update", "partial_update"]:
            # Редактировать курсы могут модераторы ИЛИ владельцы
            # Используем кастомную проверку в perform_update
            self.permission_classes = [permissions.IsAuthenticated]
        # Для retrieve и list оставляем базовый IsAuthenticated

        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """
        Автоматически привязываем курс к текущему пользователю при создании.
        """
        # Проверяем, что пользователь не модератор
        if self.request.user.groups.filter(name="moderators").exists():
            raise permissions.PermissionDenied("Модераторы не могут создавать курсы")
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        course = serializer.save()

        # Получаем всех подписчиков курса
        subscriptions = Subscription.objects.filter(course=course)
        emails = subscriptions.values_list('user__email', flat=True)

        # Отправляем письма асинхронно
        for email in emails:
            send_course_update_email.delay(course.title, email)

    def perform_destroy(self, instance):
        """
        Проверяем права на удаление.
        """
        user = self.request.user

        # Только владелец может удалять (не модератор)
        if user.groups.filter(name="moderators").exists():
            raise permissions.PermissionDenied("Модераторы не могут удалять курсы")

        if instance.owner != user:
            raise permissions.PermissionDenied("Вы не владелец этого курса")

        instance.delete()


class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MaterialsPagination

    def get_queryset(self):
        queryset = super().get_queryset()

        # Если пользователь модератор - видит все уроки
        if self.request.user.groups.filter(name="moderators").exists():
            return queryset

        # Иначе видит только свои уроки
        return queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """
        Автоматически привязываем урок к текущему пользователю при создании.
        """
        # Проверяем, что пользователь не модератор
        if self.request.user.groups.filter(name="moderators").exists():
            raise permissions.PermissionDenied("Модераторы не могут создавать уроки")
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.groups.filter(name="moderators").exists():
            return queryset
        return queryset.filter(owner=self.request.user)

    def perform_update(self, serializer):
        """Проверяем 4 часа и отправляем уведомления"""
        instance = self.get_object()
        user = self.request.user

        # Проверка прав
        if not (user.groups.filter(name="moderators").exists() or instance.owner == user):
            raise permissions.PermissionDenied("Нет прав для редактирования")

        # Сохраняем урок
        lesson = serializer.save()

        # Проверяем курс
        course = lesson.course
        time_since_update = timezone.now() - course.updated_at

        # Если курс не обновлялся > 4 часов
        if time_since_update > timedelta(hours=4):
            # Отправляем письма подписчикам
            emails = Subscription.objects.filter(course=course).values_list('user__email', flat=True)
            for email in emails:
                send_course_update_email.delay(course.title, email)

            # Обновляем время курса
            course.updated_at = timezone.now()
            course.save(update_fields=['updated_at'])

    def perform_destroy(self, instance):
        """
        Проверяем права на удаление.
        """
        user = self.request.user

        # Только владелец может удалять (не модератор)
        if user.groups.filter(name="moderators").exists():
            raise permissions.PermissionDenied("Модераторы не могут удалять уроки")

        if instance.owner != user:
            raise permissions.PermissionDenied("Вы не владелец этого урока")

        instance.delete()
