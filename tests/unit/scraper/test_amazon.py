import pytest
from scrapy.http import HtmlResponse
from scraper.spiders.amazon import AmazonSpider
from scraper.spiders.items import ProductItem
import os

def test_amazon_spider_parse():
    # Load sample HTML
    sample_path = os.path.join(os.path.dirname(__file__), "..", "..", "samples", "amazon_sample.html")
    with open(sample_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Create a fake response
    response = HtmlResponse(
        url="https://www.amazon.com/s?k=test",
        body=html_content,
        encoding="utf-8"
    )

    # Initialize spider
    spider = AmazonSpider(query="test")
    
    # Parse the response
    results = list(spider.parse(response))
    
    # Filter out items (ignoring pagination links for now if any)
    items = [res for res in results if isinstance(res, ProductItem)]
    
    # Assertions
    assert len(items) == 1
    item = items[0]
    
    assert item['title'] == "Example Product"
    assert item['price'] == 29.99
    assert item['currency'] == "$"
    assert "product-url" in item['url']
    assert item['platform'] == "amazon"
    assert item['rating'] == 4.5
