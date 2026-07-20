from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import HabitViewSet, PublicHabitListAPIView

app_name = "habits"

router = DefaultRouter(use_regex_path=False)
router.register("habits", HabitViewSet, basename="habit")

urlpatterns = [
    path("habits/public/", PublicHabitListAPIView.as_view(), name="public-habits"),
    path("", include(router.urls)),
]
