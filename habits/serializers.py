from rest_framework import serializers

from .models import Habit
from .validators import validate_habit_data


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для выполнения приватных операций CRUD, основанных на личных привычках пользователя."""

    related_habit = serializers.PrimaryKeyRelatedField(
        queryset=Habit.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Habit
        fields = (
            "id",
            "owner",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "periodicity",
            "reward",
            "execution_time",
            "is_public",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "owner", "created_at", "updated_at")

    def validate(self, attrs):
        request = self.context.get("request")
        owner = request.user if request and request.user.is_authenticated else None
        validate_habit_data(attrs, instance=self.instance, owner=owner)
        return attrs


class PublicHabitSerializer(serializers.ModelSerializer):
    """Доступная для чтения информация, не раскрывающая владельца и ссылки."""

    class Meta:
        model = Habit
        fields = (
            "id",
            "place",
            "time",
            "action",
            "is_pleasant",
            "periodicity",
            "reward",
            "execution_time",
            "is_public",
        )
        read_only_fields = fields
