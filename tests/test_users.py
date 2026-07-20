import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings

User = get_user_model()

pytestmark = pytest.mark.django_db


def test_registration_creates_user_and_hashes_password(api_client):
    response = api_client.post(
        "/api/users/register/",
        {
            "email": "new@example.com",
            "password": "very-secure-password",
            "telegram_chat_id": "555",
        },
        format="json",
    )

    assert response.status_code == 201
    user = User.objects.get(email="new@example.com")
    assert user.check_password("very-secure-password")
    assert response.data["telegram_chat_id"] == "555"


def test_jwt_authentication_uses_email(api_client, user):
    response = api_client.post(
        "/api/users/token/",
        {"email": user.email, "password": "very-secure-password"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["access"]
    assert response.data["refresh"]


def test_user_can_update_only_telegram_chat_id(authenticated_client, user):
    response = authenticated_client.patch(
        "/api/users/me/",
        {"telegram_chat_id": "777"},
        format="json",
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.telegram_chat_id == "777"


def test_cors_allows_configured_frontend(api_client):
    with override_settings(CORS_ALLOWED_ORIGINS=["http://localhost:3000"]):
        response = api_client.options(
            "/api/habits/",
            HTTP_ORIGIN="http://localhost:3000",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
        )

    assert response.status_code == 200
    assert response["access-control-allow-origin"] == "http://localhost:3000"
