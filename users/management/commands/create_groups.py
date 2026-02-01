from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from materials.models import Course, Lesson


class Command(BaseCommand):
    help = "Создает группы модераторов и назначает им права"

    def handle(self, *args, **options):
        # Создаем или получаем группу модераторов
        moderators_group, created = Group.objects.get_or_create(name="moderators")

        if created:
            self.stdout.write(self.style.SUCCESS("Группа moderators создана"))
        else:
            self.stdout.write(self.style.WARNING("Группа moderators уже существует"))

        # Получаем разрешения для курсов и уроков
        course_content_type = ContentType.objects.get_for_model(Course)
        lesson_content_type = ContentType.objects.get_for_model(Lesson)

        # Права, которые нужны модераторам: view и change (но не add и delete)
        course_permissions = Permission.objects.filter(
            content_type=course_content_type,
            codename__in=["view_course", "change_course"],
        )

        lesson_permissions = Permission.objects.filter(
            content_type=lesson_content_type,
            codename__in=["view_lesson", "change_lesson"],
        )

        # Назначаем права группе
        moderators_group.permissions.set(course_permissions | lesson_permissions)

        self.stdout.write(
            self.style.SUCCESS(
                f"Назначено {moderators_group.permissions.count()} прав группе moderators"
            )
        )
