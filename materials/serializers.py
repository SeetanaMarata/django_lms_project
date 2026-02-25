from rest_framework import serializers

from .models import Course, Lesson, Subscription


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()  # добавляем это поле

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "preview",
            "description",
            "created_at",
            "updated_at",
            "owner",
            "lessons_count",
            "lessons",
            "is_subscribed",  # добавляем is_subscribed
        ]
        read_only_fields = ["owner", "created_at", "updated_at"]

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """
        Проверяем, подписан ли текущий пользователь на этот курс.
        """
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ["id", "user", "course", "created_at"]
        read_only_fields = ["user", "created_at"]
