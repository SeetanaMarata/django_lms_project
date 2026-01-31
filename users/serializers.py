from rest_framework import serializers

from .models import Payment, User  # Добавляем User в импорт


class UserSerializer(serializers.ModelSerializer):
    # Добавляем это поле для истории платежей
    payment_history = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
            "payment_history",
        ]
        read_only_fields = ["payment_history"]

    def get_payment_history(self, obj):
        # Получаем последние 10 платежей пользователя
        payments = obj.payments.all().order_by("-payment_date")[:10]
        return PaymentSerializer(payments, many=True).data


class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    course_title = serializers.CharField(
        source="course.title", read_only=True, allow_null=True
    )
    lesson_title = serializers.CharField(
        source="lesson.title", read_only=True, allow_null=True
    )

    class Meta:
        model = Payment
        fields = [
            "id",
            "user",
            "user_email",
            "payment_date",
            "course",
            "course_title",
            "lesson",
            "lesson_title",
            "amount",
            "payment_method",
        ]
        read_only_fields = ["payment_date"]
