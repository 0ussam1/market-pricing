from __future__ import annotations

import random
from decimal import Decimal, InvalidOperation

from playwright.sync_api import Browser, BrowserContext, Playwright, sync_playwright


_playwright: Playwright | None = None
_browser: Browser | None = None
_VIEWPORTS = (
    {"width": 1280, "height": 720},
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
    {"width": 1536, "height": 864},
    {"width": 1920, "height": 1080},
)


def get_browser() -> Browser:
    global _playwright, _browser

    if _browser is None:
        _playwright = sync_playwright().start()
        _browser = _playwright.chromium.launch(headless=True)

    return _browser


def create_context(browser: Browser) -> BrowserContext:
    viewport = random.choice(_VIEWPORTS)
    return browser.new_context(viewport=viewport)


def parse_price_string(text: str | None) -> float | None:
    if not text:
        return None

    cleaned = text.strip()
    for token in ("Dhs", "DHS", "DH", "MAD", "EUR", "€", "$"):
        cleaned = cleaned.replace(token, "")

    cleaned = "".join(ch for ch in cleaned if ch.isdigit() or ch in ",.")
    if not cleaned:
        return None

    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(".") > cleaned.rfind(","):
            cleaned = cleaned.replace(",", "")
        else:
            cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned:
        tail = cleaned.rsplit(",", 1)[-1]
        if len(tail) == 2:
            cleaned = cleaned.replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif "." in cleaned:
        tail = cleaned.rsplit(".", 1)[-1]
        if len(tail) == 3:
            cleaned = cleaned.replace(".", "")
    if not cleaned:
        return None

    try:
        return float(Decimal(cleaned))
    except (InvalidOperation, ValueError):
        return None


def close_browser() -> None:
    global _playwright, _browser

    if _browser is not None:
        _browser.close()
        _browser = None

    if _playwright is not None:
        _playwright.stop()
        _playwright = None
