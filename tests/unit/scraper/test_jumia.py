from pathlib import Path

from scraper.base import parse_price_string
from scraper.jumia import extract_jumia_results


def test_extract_jumia_results_from_fixture():
    fixture_path = (
        Path(__file__).resolve().parents[2] / "fixtures" / "jumia_results.html"
    )
    html = fixture_path.read_text(encoding="utf-8")

    results = extract_jumia_results(html)

    assert len(results) == 2

    assert results[0] == {
        "title": "Apple iPhone 15 128 Go Noir",
        "price": 12999.0,
        "currency": "MAD",
        "url": "https://www.jumia.ma/apple-iphone-15-128-go-noir-123456.html",
        "platform": "jumia",
        "rating": 4.5,
    }

    assert results[1]["title"] == "Samsung Galaxy A55 256 Go"
    assert results[1]["price"] == 5490.0
    assert results[1]["currency"] == "MAD"
    assert results[1]["platform"] == "jumia"
    assert results[1]["rating"] == 4.0


def test_parse_price_string_handles_common_formats():
    assert parse_price_string("12,999 Dhs") == 12999.0
    assert parse_price_string("5.490 DH") == 5490.0
    assert parse_price_string("$1,299.50") == 1299.50
    assert parse_price_string(None) is None
