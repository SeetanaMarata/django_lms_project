from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Payment, User
from .permissions import IsModerator, IsOwner
from .serializers import (PaymentSerializer, UserDetailSerializer,
                          UserPublicSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """
        Выбираем сериализатор в зависимости от действия и прав.
        """
        if self.action == "retrieve":
            # Для просмотра детальной информации
            # Если пользователь смотрит свой профиль или он модератор - полная информация
            # Иначе - публичная информация
            obj = self.get_object()
            if obj == self.request.user or IsModerator().has_permission(
                self.request, self
            ):
                return UserDetailSerializer
            else:
                return UserPublicSerializer
        elif self.action == "update" or self.action == "partial_update":
            # Для редактирования всегда используем UserDetailSerializer
            return UserDetailSerializer
        elif self.action == "create":
            # Для создания (регистрации) тоже UserDetailSerializer
            return UserDetailSerializer
        else:
            # Для списка используем публичный сериализатор
            return UserPublicSerializer

    def get_permissions(self):
        """
        Настраиваем права доступа.
        """
        if self.action == "create":
            # Создавать пользователей может кто угодно (регистрация)
            # Но у нас регистрация отдельно, так что здесь можно оставить ограничение
            self.permission_classes = [permissions.AllowAny]
        elif self.action in ["update", "partial_update", "destroy"]:
            # Редактировать и удалять могут только владельцы или модераторы
            self.permission_classes = [
                permissions.IsAuthenticated,
                IsModerator | IsOwner,
            ]
        elif self.action in ["retrieve", "list"]:
            # Просматривать могут все авторизованные
            self.permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in self.permission_classes]

    @action(detail=False, methods=["get"])
    def me(self, request):
        """
        Эндпоинт для получения информации о текущем пользователе.
        """
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)


class UserCreateAPIView(generics.CreateAPIView):
    """
    Контроллер для регистрации нового пользователя.
    Доступен без аутентификации.
    """

    serializer_class = (
        UserDetailSerializer  # Используем UserDetailSerializer для создания
    )
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        user.set_password(serializer.validated_data["password"])
        user.save()


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
