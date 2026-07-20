from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from habits.models import Habit, HabitNotification
from habits.tasks import is_habit_due_on_date, send_habit_reminders

pytestmark = pytest.mark.django_db


def create_habit_for_current_minute(user, **extra_fields):
    now = timezone.localtime()
    defaults = {
        "owner": user,
        "place": "Дома",
        "time": now.time().replace(second=0, microsecond=0),
        "action": "Прочитать 10 страниц книги",
        "execution_time": 120,
    }
    defaults.update(extra_fields)
    return Habit.objects.create(**defaults)


@patch("habits.tasks.send_telegram_message", return_value=True)
def test_task_sends_once_and_prevents_duplicate_notification(mock_send, user):
    habit = create_habit_for_current_minute(user)

    first_result = send_habit_reminders.run()
    second_result = send_habit_reminders.run()

    assert first_result["sent"] == 1
    assert second_result["sent"] == 0
    assert second_result["skipped"] == 1
    assert mock_send.call_count == 1
    assert HabitNotification.objects.filter(habit=habit).count() == 1
    message = mock_send.call_args.args[1]
    assert "Место: Дома" in message
    assert "Действие: Прочитать 10 страниц книги" in message


@patch("habits.tasks.send_telegram_message", return_value=True)
def test_task_respects_periodicity(mock_send, user):
    habit = create_habit_for_current_minute(user, periodicity=2)
    Habit.objects.filter(pk=habit.pk).update(
        created_at=timezone.now() - timedelta(days=1)
    )
    habit.refresh_from_db()

    result = send_habit_reminders.run()

    assert result["sent"] == 0
    assert result["skipped"] == 1
    mock_send.assert_not_called()
    assert not HabitNotification.objects.filter(habit=habit).exists()


@patch("habits.tasks.send_telegram_message", side_effect=RuntimeError("network down"))
def test_task_records_failure_without_creating_notification(mock_send, user):
    habit = create_habit_for_current_minute(user)

    result = send_habit_reminders.run()

    assert result["failed"] == 1
    mock_send.assert_called_once()
    assert not HabitNotification.objects.filter(habit=habit).exists()


def test_due_helper_uses_creation_date_and_periodicity(user):
    habit = create_habit_for_current_minute(user, periodicity=3)
    created_date = timezone.localtime(habit.created_at).date()

    assert is_habit_due_on_date(habit, created_date)
    assert is_habit_due_on_date(habit, created_date + timedelta(days=3))
    assert not is_habit_due_on_date(habit, created_date + timedelta(days=1))
