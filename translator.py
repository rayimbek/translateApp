
import logging, httpx
import asyncio
import pprint as pp

log = logging.getLogger(__name__)

API1_URL = "http://34.9.223.19:8000/translate/ru-kk/"
API2_URL = "http://34.9.223.19:8000/translate/kk-ru/"

class TranslationError(RuntimeError):
    ...


async def translate_text_block(text: str) -> str:
    if not text.strip():
        return text

    async with httpx.AsyncClient(timeout=200) as client:
        try:
            resp = await client.post(API1_URL, json={"text": text})
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            # здесь уже есть exc.request и exc.response
            log.error(
                "API1 %s %s -> %d\nHeaders: %s\nBody: %s",
                exc.request.method,
                exc.request.url,
                exc.response.status_code,
                exc.response.headers,
                exc.response.text[:500],  # обрезаем, чтобы лог был короче
            )
            raise TranslationError(
                f"API1 вернул {exc.response.status_code}"
            ) from exc
        except httpx.TimeoutException as exc:
            raise TranslationError("API1: тайм‑аут") from exc
        except httpx.HTTPError as exc:  # всё остальное (DNS, Connect, TLS…)
            raise TranslationError(f"HTTP‑сбой: {exc}") from exc

    pp.pprint(resp)
    data = resp.json()
    return data.get("translated_text") or text
