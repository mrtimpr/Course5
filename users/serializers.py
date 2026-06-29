from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """Безопасное представление текущего пользователя."""

    class Meta:
        model = User
        fields = ("id", "email", "telegram_chat_id")
        read_only_fields = ("id", "email")


class RegistrationSerializer(serializers.ModelSerializer):
    """Создайте пользователя с надежно хешированным паролем."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "email", "password", "telegram_chat_id")
        read_only_fields = ("id",)

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)
