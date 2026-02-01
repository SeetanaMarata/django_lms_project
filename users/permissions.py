from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """
    Проверяет, является ли пользователь модератором.
    Модератор - пользователь, состоящий в группе 'moderators'.
    """

    def has_permission(self, request, view):
        # Проверяем, авторизован ли пользователь
        if not request.user.is_authenticated:
            return False

        # Проверяем, состоит ли пользователь в группе moderators
        return request.user.groups.filter(name="moderators").exists()


class IsOwner(permissions.BasePermission):
    """
    Проверяет, является ли пользователь владельцем объекта.
    """

    def has_object_permission(self, request, view, obj):
        # Проверяем, есть ли у объекта поле owner
        # и совпадает ли оно с текущим пользователем
        return obj.owner == request.user
