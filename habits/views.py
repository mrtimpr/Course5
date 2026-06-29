from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Habit
from .serializers import HabitSerializer, PublicHabitSerializer


@extend_schema_view(
    list=extend_schema(summary="Список привычек текущего пользователя"),
    create=extend_schema(summary="Создание привычки"),
    retrieve=extend_schema(summary="Получение своей привычки"),
    update=extend_schema(summary="Полное изменение своей привычки"),
    partial_update=extend_schema(summary="Частичное изменение своей привычки"),
    destroy=extend_schema(summary="Удаление своей привычки"),
)
class HabitViewSet(viewsets.ModelViewSet):
    """CRUD-интерфейс доступен только авторизованному владельцу привычки."""

    serializer_class = HabitSerializer
    permission_classes = (IsAuthenticated,)
    lookup_value_converter = "int"

    def get_queryset(self):
        return Habit.objects.filter(owner=self.request.user).select_related(
            "related_habit"
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


@extend_schema(
    tags=["Habits"],
    summary="Список публичных привычек",
    responses=PublicHabitSerializer(many=True),
)
class PublicHabitListAPIView(ListAPIView):
    """Список привычек, помеченных как общедоступные, доступен только для чтения и отображается с постраничной разбивкой."""

    serializer_class = PublicHabitSerializer
    permission_classes = (AllowAny,)
    queryset = Habit.objects.filter(is_public=True)
