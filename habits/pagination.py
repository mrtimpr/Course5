from rest_framework.pagination import LimitOffsetPagination


class HabitPagination(LimitOffsetPagination):
    """По умолчанию возвращаются пять привычек, поддерживаются параметры запроса limit/offset."""

    default_limit = 5
    max_limit = 100
