from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus, urljoin

from parsel import Selector

from .base import create_context, parse_price_string


BASE_URL = "https://www.jumia.ma"
SEARCH_URL = f"{BASE_URL}/catalog/?q={{query}}"
PRODUCT_CARD_SELECTOR = ".c-product-item"
MAX_PAGES = 3


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(value.split())
    return cleaned or None


def _parse_price(price_text: str | None) -> tuple[float | None, str | None]:
    cleaned = _clean_text(price_text)
    if not cleaned:
        return None, None

    currency = "MAD" if "DH" in cleaned.upper() else None
    price = parse_price_string(cleaned)
    return price, currency


def _parse_rating(rating_text: str | None) -> float | None:
    cleaned = _clean_text(rating_text)
    if not cleaned:
        return None

    token = cleaned.split(" out")[0].split("/")[0].strip()
    try:
        return float(token)
    except ValueError:
        return None


def extract_jumia_results(html: str) -> list[dict[str, Any]]:
    selector = Selector(text=html)
    results: list[dict[str, Any]] = []

    for card in selector.css(PRODUCT_CARD_SELECTOR):
        title = _clean_text(card.css(".info .name::text, .name::text").get())
        raw_price = card.css(".prc::text").get()
        price, currency = _parse_price(raw_price)
        url = card.css("a.core::attr(href), a::attr(href)").get()
        rating = _parse_rating(
            card.css(
                ".stars._s::attr(aria-label), .stars::attr(aria-label), .rev::text"
            ).get()
        )

        if not title or not url or price is None:
            continue

        results.append(
            {
                "title": title,
                "price": price,
                "currency": currency or "MAD",
                "url": urljoin(BASE_URL, url),
                "platform": "jumia",
                "rating": rating,
            }
        )

    return results


def _extract_next_page_url(page) -> str | None:
    next_href = page.locator('a[aria-label="Next Page"]').get_attribute("href")
    if not next_href:
        return None
    return urljoin(BASE_URL, next_href)


def scrape_jumia(query: str, browser) -> list[dict[str, Any]]:
    context = create_context(browser)
    page = context.new_page()
    results: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    try:
        next_url = SEARCH_URL.format(query=quote_plus(query))

        for _ in range(MAX_PAGES):
            page.goto(next_url, wait_until="domcontentloaded")
            page.wait_for_selector(PRODUCT_CARD_SELECTOR, timeout=15000)

            for item in extract_jumia_results(page.content()):
                if item["url"] in seen_urls:
                    continue
                seen_urls.add(item["url"])
                results.append(item)

            next_url = _extract_next_page_url(page)
            if not next_url:
                break

        return results
    finally:
        page.close()
        context.close()
