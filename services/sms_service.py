import os
import random
import logging

logger = logging.getLogger(__name__)

AT_USERNAME = os.getenv("AT_USERNAME", "sandbox")
AT_API_KEY = os.getenv("AT_API_KEY", "")
DEV_MODE = os.getenv("DEV_MODE", "true").lower() == "true"

_at = None


def _get_at():
    global _at
    if _at is None and AT_API_KEY:
        try:
            import africastalking
            africastalking.initialize(AT_USERNAME, AT_API_KEY)
            _at = africastalking.SMS
        except Exception as e:
            logger.error(f"Africa's Talking init failed: {e}")
    return _at


def generate_otp() -> str:
    return str(random.randint(100000, 999999))


async def send_otp(phone: str, code: str) -> bool:
    if DEV_MODE or not AT_API_KEY:
        logger.info(f"[DEV] OTP for {phone}: {code}")
        return True

    sms = _get_at()
    if not sms:
        logger.warning("SMS service unavailable — OTP not sent")
        return False

    try:
        formatted = phone if phone.startswith("+") else f"+250{phone.lstrip('0')}"
        response = sms.send(
            message=f"Your EZA AI code is {code}. Valid for 10 minutes. Do not share.",
            recipients=[formatted],
            sender_id="EZAAI",
        )
        logger.info(f"SMS sent: {response}")
        return True
    except Exception as e:
        logger.error(f"SMS send failed: {e}")
        return False
