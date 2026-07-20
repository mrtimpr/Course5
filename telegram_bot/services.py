import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class TelegramAPIError(RuntimeError):
    """Эта ошибка возникает, когда Telegram отправляет некорректный ответ через API."""


def send_telegram_message(chat_id: str, text: str) -> bool:
    """Отправьте текстовое сообщение и верните информацию о том, был ли успешно выполнен вызов API."""
    token = settings.TELEGRAM_BOT_TOKEN
    if not token or not chat_id:
        logger.warning("Telegram reminder skipped: bot token or chat ID is not set.")
        return False

    url = f"{settings.TELEGRAM_API_URL.rstrip('/')}/bot{token}/sendMessage"
    response = requests.post(
        url,
        json={"chat_id": chat_id, "text": text},
        timeout=settings.TELEGRAM_REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("ok"):
        raise TelegramAPIError(payload.get("description", "Telegram API error"))
    return True
