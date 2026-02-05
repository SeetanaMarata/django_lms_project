from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from materials.views import CourseViewSet
# !!! ИМПОРТИРУЕМ PaymentViewSet !!!
from users.views import PaymentViewSet, UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"courses", CourseViewSet)
router.register(r"payments", PaymentViewSet)  # Теперь PaymentViewSet доступен

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/lessons/", include("materials.urls")),
    path("api/auth/", include("users.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
