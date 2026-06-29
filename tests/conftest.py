from datetime import time

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="owner@example.com",
        password="very-secure-password",
        telegram_chat_id="10001",
    )


@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        email="another@example.com",
        password="another-secure-password",
        telegram_chat_id="10002",
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def habit_payload():
    return {
        "place": "Дома",
        "time": time(19, 0).isoformat(),
        "action": "Прочитать 10 страниц книги",
        "is_pleasant": False,
        "periodicity": 1,
        "reward": "Чашка чая",
        "execution_time": 120,
        "is_public": False,
    }
