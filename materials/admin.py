from django.contrib import admin

from .models import Course, Lesson


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "created_at", "updated_at")
    search_fields = ("title", "description")
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "course", "owner")
    list_filter = ("course",)
    search_fields = ("title", "description")
