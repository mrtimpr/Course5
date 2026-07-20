from collections.abc import Mapping
from typing import Any

from rest_framework import serializers

MAX_EXECUTION_TIME_SECONDS = 120
MAX_PERIODICITY_DAYS = 7


def _resolved_value(
    attrs: Mapping[str, Any],
    instance: Any,
    field_name: str,
    default: Any = None,
) -> Any:
    """Получить значение из частично обновленных данных или из существующего экземпляра."""
    if field_name in attrs:
        return attrs[field_name]
    if instance is not None:
        return getattr(instance, field_name)
    return default


def validate_habit_data(
    attrs: Mapping[str, Any],
    *,
    instance: Any = None,
    owner: Any = None,
) -> None:
    """Проверьте все требования, предъявляемые к различным полям данных, которые определены для данной привычки."""
    is_pleasant = _resolved_value(attrs, instance, "is_pleasant", False)
    related_habit = _resolved_value(attrs, instance, "related_habit")
    reward = _resolved_value(attrs, instance, "reward", "")
    periodicity = _resolved_value(attrs, instance, "periodicity", 1)
    execution_time = _resolved_value(attrs, instance, "execution_time")

    errors: dict[str, list[str]] = {}

    if reward and related_habit:
        errors.setdefault("non_field_errors", []).append(
            "Нельзя одновременно указывать вознаграждение и связанную привычку."
        )

    if execution_time is not None and execution_time > MAX_EXECUTION_TIME_SECONDS:
        errors.setdefault("execution_time", []).append(
            "Время выполнения привычки не может превышать 120 секунд."
        )

    if periodicity is None or not 1 <= periodicity <= MAX_PERIODICITY_DAYS:
        errors.setdefault("periodicity", []).append(
            "Периодичность должна быть указана в диапазоне от 1 до 7 дней."
        )

    if related_habit:
        if not related_habit.is_pleasant:
            errors.setdefault("related_habit", []).append(
                "Связанной может быть только приятная привычка."
            )
        if owner is not None and related_habit.owner_id != owner.id:
            errors.setdefault("related_habit", []).append(
                "Можно связывать только собственные привычки."
            )
        if instance is not None and related_habit.pk == instance.pk:
            errors.setdefault("related_habit", []).append(
                "Привычка не может быть связана сама с собой."
            )

    if is_pleasant and reward:
        errors.setdefault("reward", []).append(
            "У приятной привычки не может быть вознаграждения."
        )

    if is_pleasant and related_habit:
        errors.setdefault("related_habit", []).append(
            "У приятной привычки не может быть связанной привычки."
        )

    if errors:
        raise serializers.ValidationError(errors)
