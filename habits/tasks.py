import logging
from datetime import date

from celery import shared_task
from django.db import IntegrityError, transaction
from django.utils import timezone

from telegram_bot.services import send_telegram_message

from .models import Habit, HabitNotification

logger = logging.getLogger(__name__)


def is_habit_due_on_date(habit: Habit, target_date: date) -> bool:
    """Укажите, следует ли выполнять данную привычку в целевую дату."""
    start_date = timezone.localtime(habit.created_at).date()
    elapsed_days = (target_date - start_date).days
    return elapsed_days >= 0 and elapsed_days % habit.periodicity == 0


def build_reminder_text(habit: Habit) -> str:
    """Отформатируйте текст уведомлений Telegram в соответствии с вашей привычкой."""
    return (
        "Напоминание о привычке\n\n"
        f"Время: {habit.time:%H:%M}\n"
        f"Место: {habit.place}\n"
        f"Действие: {habit.action}"
    )


@shared_task(name="habits.tasks.send_habit_reminders")
def send_habit_reminders() -> dict[str, int]:
    """Отправляйте напоминания о сроках выполнения один раз для каждой привычки и даты.

    Celery Beat запускает эту задачу каждую минуту. Уникальное ограничение базы данных предотвращает
    дублирование сообщений, если задача случайно отправляется более одного раза.
    """
    now = timezone.localtime()
    due_habits = Habit.objects.select_related("owner").filter(
        time__hour=now.hour,
        time__minute=now.minute,
    )

    result = {"checked": 0, "sent": 0, "skipped": 0, "failed": 0}
    for habit in due_habits:
        result["checked"] += 1
        if not habit.owner.telegram_chat_id or not is_habit_due_on_date(
            habit,
            now.date(),
        ):
            result["skipped"] += 1
            continue

        try:
            with transaction.atomic():
                notification = HabitNotification.objects.create(
                    habit=habit,
                    scheduled_date=now.date(),
                )

                was_sent = send_telegram_message(
                    habit.owner.telegram_chat_id,
                    build_reminder_text(habit),
                )
                if not was_sent:
                    notification.delete()
                    result["skipped"] += 1
                    continue
        except IntegrityError:
            result["skipped"] += 1
        except Exception:
            logger.exception("Could not send reminder for habit %s.", habit.pk)
            result["failed"] += 1
        else:
            result["sent"] += 1

    return result
