from django.contrib import admin

from .models import Habit, HabitNotification


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "action",
        "time",
        "periodicity",
        "is_pleasant",
        "is_public",
    )
    list_filter = ("is_pleasant", "is_public", "periodicity")
    search_fields = ("action", "place", "owner__email")


@admin.register(HabitNotification)
class HabitNotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "habit", "scheduled_date", "sent_at")
    list_filter = ("scheduled_date",)
