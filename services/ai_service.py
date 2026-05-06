import os
import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

HF_SPACE_URL = os.getenv("AI_SERVICE_URL", "https://ezaaimuhinzi-ezaai.hf.space")
_TIMEOUT = httpx.Timeout(90.0, connect=30.0)

_SUPPORTED_CROPS = {"Corn", "Tomato", "Potato", "Pepper"}


async def predict_disease(image_bytes: bytes, crop_filter: Optional[str] = None) -> dict:
    files = {"file": ("scan.jpg", image_bytes, "image/jpeg")}
    data = {}
    if crop_filter and crop_filter in _SUPPORTED_CROPS:
        data["crop_filter"] = crop_filter

    for attempt in range(4):
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.post(f"{HF_SPACE_URL}/predict", files=files, data=data)
            if resp.status_code == 503 and attempt < 3:
                import asyncio
                await asyncio.sleep(20)
                continue
            resp.raise_for_status()
            return resp.json()
        except httpx.TimeoutException:
            if attempt == 3:
                raise
            import asyncio
            await asyncio.sleep(10)
        except Exception as e:
            logger.error(f"AI service error (attempt {attempt + 1}): {e}")
            if attempt == 3:
                raise

    raise RuntimeError("AI service unavailable after retries")
