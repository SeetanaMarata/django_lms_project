from rest_framework import serializers

from .models import Payment, User


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


# !!! СТАРЫЙ UserSerializer переименуем в UserDetailSerializer !!!
class UserDetailSerializer(serializers.ModelSerializer):
    """
    Полная информация о пользователе (для владельца и модераторов).
    """

    payment_history = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "phone",
            "city",
            "avatar",
            "first_name",
            "last_name",
            "password",
            "payment_history",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def get_payment_history(self, obj):
        """
        Возвращает историю платежей пользователя
        """
        payments = obj.payments.all().order_by("-payment_date")[:10]
        return PaymentSerializer(payments, many=True).data


# !!! СОЗДАЕМ НОВЫЙ ДЛЯ ПУБЛИЧНОГО ПРОСМОТРА !!!
class UserPublicSerializer(serializers.ModelSerializer):
    """
    Публичная информация о пользователе (для просмотра другими пользователями).
    Не включает: пароль, фамилию, историю платежей.
    """

    class Meta:
        model = User
        fields = ("id", "email", "phone", "city", "avatar", "first_name")
        read_only_fields = fields  # Все поля только для чтения


class PaymentCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания платежа через Stripe.
    """

    course_id = serializers.IntegerField(write_only=True, required=False)
    lesson_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Payment
        fields = ("course_id", "lesson_id", "amount", "payment_method")
        read_only_fields = (
            "user",
            "payment_date",
            "stripe_product_id",
            "stripe_price_id",
            "stripe_session_id",
            "stripe_payment_status",
            "stripe_payment_url",
        )

    def validate(self, data):
        """
        Валидация: должен быть указан либо курс, либо урок.
        """
        course_id = data.get("course_id")
        lesson_id = data.get("lesson_id")

        if not course_id and not lesson_id:
            raise serializers.ValidationError(
                "Необходимо указать course_id или lesson_id"
            )

        if course_id and lesson_id:
            raise serializers.ValidationError("Укажите только курс ИЛИ урок")

        return data

    def create(self, validated_data):
        # Этот метод будет переопределен во view
        pass
