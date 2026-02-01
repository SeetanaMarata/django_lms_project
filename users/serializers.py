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
