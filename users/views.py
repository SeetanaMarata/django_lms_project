from decimal import Decimal

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from materials.models import Course, Lesson
from services.stripe_service import (
    create_stripe_checkout_session,
    create_stripe_price,
    create_stripe_product,
)

from .filters import PaymentFilter
from .models import Payment, User
from .permissions import IsModerator, IsOwner
from .serializers import (
    PaymentCreateSerializer,
    PaymentSerializer,
    UserDetailSerializer,
    UserPublicSerializer,
)


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
    """
    ViewSet для работы с платежами.

    Доступные действия:
    - list: Получить список платежей с фильтрацией
    - retrieve: Получить детальную информацию о платеже
    - create: Создать новый платеж

    Фильтрация (query parameters):
    - ?ordering=payment_date (или -payment_date для DESC)
    - ?course_id=1 - фильтр по курсу
    - ?lesson_id=1 - фильтр по уроку
    - ?payment_method=cash|transfer - фильтр по способу оплаты

    Примеры запросов:
    - GET /api/payments/?ordering=-payment_date
    - GET /api/payments/?course_id=1&payment_method=transfer
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ["payment_date"]
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=["Платежи"],
        operation_description="Создать платеж через Stripe и получить ссылку для оплаты",
        request_body=PaymentCreateSerializer,
        responses={
            201: openapi.Response(
                description="Платеж создан, ссылка на оплату сгенерирована",
                examples={
                    "application/json": {
                        "id": 1,
                        "stripe_payment_url": "https://checkout.stripe.com/pay/cs_test_...",
                        "message": "Для оплаты перейдите по ссылке",
                    }
                },
            ),
            400: openapi.Response(
                description="Ошибка валидации",
                examples={
                    "application/json": {
                        "error": "Необходимо указать course_id или lesson_id"
                    }
                },
            ),
        },
    )
    @action(detail=False, methods=["post"], url_path="create-stripe-payment")
    def create_stripe_payment(self, request):
        """
        Создает платеж и сессию оплаты в Stripe.
        Возвращает ссылку для оплаты.
        """
        serializer = PaymentCreateSerializer(
            data=request.data, context={"request": request}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        # Получаем данные
        user = request.user
        course_id = serializer.validated_data.get("course_id")
        lesson_id = serializer.validated_data.get("lesson_id")
        amount = Decimal(str(serializer.validated_data["amount"]))

        # Получаем курс или урок
        if course_id:
            product_obj = get_object_or_404(Course, id=course_id)
            product_name = f"Курс: {product_obj.title}"
        else:
            product_obj = get_object_or_404(Lesson, id=lesson_id)
            product_name = f"Урок: {product_obj.title}"

        try:
            # 1. Создаем продукт в Stripe
            stripe_product = create_stripe_product(
                name=product_name,
                description=(
                    product_obj.description[:500]
                    if product_obj.description
                    else product_name
                ),
            )

            # 2. Создаем цену в Stripe
            stripe_price = create_stripe_price(
                product_id=stripe_product.id, amount=amount
            )

            # 3. Создаем сессию оплаты в Stripe
            success_url = f"{request.build_absolute_uri('/')}api/payments/success/"
            cancel_url = f"{request.build_absolute_uri('/')}api/payments/cancel/"

            metadata = {
                "user_id": str(user.id),
                "user_email": user.email,
                "product_type": "course" if course_id else "lesson",
                "product_id": str(course_id or lesson_id),
            }

            stripe_session = create_stripe_checkout_session(
                price_id=stripe_price.id,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata,
            )

            # 4. Создаем запись платежа в нашей БД
            payment = Payment.objects.create(
                user=user,
                course=product_obj if course_id else None,
                lesson=product_obj if lesson_id else None,
                amount=amount,
                payment_method="stripe",
                stripe_product_id=stripe_product.id,
                stripe_price_id=stripe_price.id,
                stripe_session_id=stripe_session.id,
                stripe_payment_status="pending",
                stripe_payment_url=stripe_session.url,
            )

            return Response(
                {
                    "id": payment.id,
                    "stripe_payment_url": stripe_session.url,
                    "message": "Для оплаты перейдите по ссылке",
                },
                status=201,
            )

        except Exception as e:
            return Response({"error": f"Ошибка создания платежа: {str(e)}"}, status=500)

    @swagger_auto_schema(
        tags=["Платежи"],
        operation_description="Проверить статус платежа в Stripe",
        responses={
            200: openapi.Response(
                description="Статус платежа",
                examples={
                    "application/json": {
                        "payment_id": 1,
                        "stripe_session_id": "cs_test_...",
                        "status": "paid",
                        "paid": True,
                        "amount_total": 10000,
                        "currency": "rub",
                    }
                },
            ),
            404: openapi.Response(
                description="Платеж не найден",
                examples={"application/json": {"error": "Платеж не найден"}},
            ),
        },
    )
    @action(detail=True, methods=["get"], url_path="check-status")
    def check_payment_status(self, request, pk=None):
        """
        Проверяет статус платежа в Stripe.
        """
        payment = self.get_object()

        if not payment.stripe_session_id:
            return Response(
                {"error": "Этот платеж не был создан через Stripe"}, status=400
            )

        try:
            from services.stripe_service import get_stripe_session_status

            status_info = get_stripe_session_status(payment.stripe_session_id)

            # Обновляем статус в нашей БД
            payment.stripe_payment_status = status_info["status"]
            payment.save()

            return Response(
                {
                    "payment_id": payment.id,
                    "stripe_session_id": payment.stripe_session_id,
                    **status_info,
                }
            )

        except Exception as e:
            return Response({"error": f"Ошибка проверки статуса: {str(e)}"}, status=500)
