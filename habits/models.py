from django.conf import settings
from django.db import models


class Habit(models.Model):
    """Полезная или приятная привычка, запланированная на определенное время и место."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="Пользователь",
    )
    place = models.CharField("Место", max_length=255)
    time = models.TimeField("Время", db_index=True)
    action = models.CharField("Действие", max_length=500)
    is_pleasant = models.BooleanField("Приятная привычка", default=False)
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="useful_habits",
        verbose_name="Связанная привычка",
    )
    periodicity = models.PositiveSmallIntegerField("Периодичность", default=1)
    reward = models.CharField("Вознаграждение", max_length=255, blank=True, default="")
    execution_time = models.PositiveSmallIntegerField(
        "Время выполнения в секундах",
    )
    is_public = models.BooleanField("Опубликована", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("time", "id")
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"

    def __str__(self) -> str:
        return f"{self.action} — {self.time:%H:%M}"


class HabitNotification(models.Model):
    """Отправленное напоминание, используемое для предотвращения повторных сообщений в один и тот же день."""

    habit = models.ForeignKey(
        Habit,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    scheduled_date = models.DateField("Дата напоминания")
    sent_at = models.DateTimeField("Отправлено", auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("habit", "scheduled_date"),
                name="unique_habit_notification_per_date",
            )
        ]
        verbose_name = "Уведомление о привычке"
        verbose_name_plural = "Уведомления о привычках"

    def __str__(self) -> str:
        return f"{self.habit_id}: {self.scheduled_date}"
