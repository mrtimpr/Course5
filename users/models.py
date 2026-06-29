from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Менеджер для пользователей, аутентифицированных по электронной почте."""

    use_in_migrations = True

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        """Создайте и сохраните данные обычного пользователя."""
        if not email:
            raise ValueError("Для пользователя необходимо указать email.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        password: str | None = None,
        **extra_fields,
    ):
        """Создайте и сохраните права суперпользователя."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("У суперпользователя is_staff должен быть True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("У суперпользователя is_superuser должен быть True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Пользователь приложения идентифицируется по уникальному адресу электронной почты."""

    username = None
    email = models.EmailField("email", unique=True)
    telegram_chat_id = models.CharField(
        "ID чата Telegram",
        max_length=100,
        blank=True,
        default="",
        help_text="ID личного чата с ботом для получения напоминаний.",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()

    def __str__(self) -> str:
        return self.email
