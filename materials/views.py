from rest_framework import generics, permissions, viewsets

from users.permissions import IsModerator, IsOwner

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Возвращаем queryset в зависимости от прав пользователя.
        """
        queryset = super().get_queryset()

        # Если пользователь модератор - видит все курсы
        if IsModerator().has_permission(self.request, self):
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
            # Удалять курсы могут только владельцы (не модераторы)
            self.permission_classes = [
                permissions.IsAuthenticated,
                ~IsModerator,
                IsOwner,
            ]
        elif self.action in ["update", "partial_update"]:
            # Редактировать курсы могут модераторы ИЛИ владельцы
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsModerator | IsOwner,
            ]
        # Для retrieve и list оставляем базовый IsAuthenticated

        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """
        Автоматически привязываем курс к текущему пользователю при создании.
        """
        serializer.save(owner=self.request.user)


class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Если пользователь модератор - видит все уроки
        if IsModerator().has_permission(self.request, self):
            return queryset

        # Иначе видит только свои уроки
        return queryset.filter(owner=self.request.user)

    def get_permissions(self):
        if self.request.method == "POST":
            # Создавать уроки могут только не-модераторы
            return [permissions.IsAuthenticated(), ~IsModerator()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        """
        Автоматически привязываем урок к текущему пользователю при создании.
        """
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Если пользователь модератор - видит все уроки
        if IsModerator().has_permission(self.request, self):
            return queryset

        # Иначе видит только свои уроки
        return queryset.filter(owner=self.request.user)

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            # Редактировать могут модераторы ИЛИ владельцы
            return [permissions.IsAuthenticated(), IsModerator() | IsOwner()]
        elif self.request.method == "DELETE":
            # Удалять могут только владельцы (не модераторы)
            return [permissions.IsAuthenticated(), ~IsModerator(), IsOwner()]
        # GET запросы (просмотр) доступны всем авторизованным
        return [permissions.IsAuthenticated()]
