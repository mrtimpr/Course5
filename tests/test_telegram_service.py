from unittest.mock import Mock, patch

import pytest
from django.test import override_settings

from telegram_bot.services import TelegramAPIError, send_telegram_message


def test_service_skips_message_without_token_or_chat_id():
    with override_settings(TELEGRAM_BOT_TOKEN=""):
        assert send_telegram_message("123", "hello") is False

    with override_settings(TELEGRAM_BOT_TOKEN="token"):
        assert send_telegram_message("", "hello") is False


@patch("telegram_bot.services.requests.post")
def test_service_sends_successful_request(mock_post):
    response = Mock()
    response.json.return_value = {"ok": True}
    mock_post.return_value = response

    with override_settings(
        TELEGRAM_BOT_TOKEN="secret-token",
        TELEGRAM_API_URL="https://api.telegram.org/",
        TELEGRAM_REQUEST_TIMEOUT=7,
    ):
        result = send_telegram_message("123", "hello")

    assert result is True
    mock_post.assert_called_once_with(
        "https://api.telegram.org/botsecret-token/sendMessage",
        json={"chat_id": "123", "text": "hello"},
        timeout=7,
    )
    response.raise_for_status.assert_called_once()


@patch("telegram_bot.services.requests.post")
def test_service_raises_for_telegram_api_error(mock_post):
    response = Mock()
    response.json.return_value = {"ok": False, "description": "Bad Request"}
    mock_post.return_value = response

    with override_settings(TELEGRAM_BOT_TOKEN="secret-token"):
        with pytest.raises(TelegramAPIError, match="Bad Request"):
            send_telegram_message("123", "hello")
