import json

from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course, Subscription
from .serializers import SubscriptionSerializer


class SubscriptionAPIView(APIView):
    """
    API для управления подпиской пользователя на курс
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print(f"=== DEBUG SubscriptionAPIView ===")
        print(f"Пользователь: {request.user.email}")
        print(f"Данные запроса: {request.data}")
        print(f"Тип данных: {type(request.data)}")

        user = request.user
        course_id = request.data.get("course_id")

        if not course_id:
            print("❌ Ошибка: course_id не передан")
            return Response({"error": "course_id обязателен"}, status=400)

        print(f"Ищем курс с ID: {course_id}")

        try:
            course = get_object_or_404(Course, id=course_id)
        except Exception as e:
            print(f"❌ Ошибка поиска курса: {e}")
            return Response({"error": f"Курс не найден: {str(e)}"}, status=404)

        print(f"Найден курс: {course.title}")

        # Проверяем, есть ли уже подписка
        subscription = Subscription.objects.filter(user=user, course=course)

        if subscription.exists():
            # Если подписка есть - удаляем её
            print(f"✅ Подписка найдена, удаляем...")
            subscription.delete()
            message = "Подписка удалена"
            status = 200
        else:
            # Если подписки нет - создаём
            print(f"✅ Подписки нет, создаём...")
            try:
                Subscription.objects.create(user=user, course=course)
                message = "Подписка добавлена"
                status = 201
            except Exception as e:
                print(f"❌ Ошибка создания подписки: {e}")
                return Response({"error": f"Ошибка создания: {str(e)}"}, status=400)

        print(f"=== КОНЕЦ DEBUG ===")
        return Response({"message": message}, status=status)
