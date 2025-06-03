import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text}
    try:
        response = requests.post(url, json=payload)
        result = response.json()
        if not result.get("ok"):
            logger.error(f"Telegram error: {result}")
    except Exception as e:
        logger.exception(f"Telegramga yuborishda xatolik: {e}")
