import pytest
import os
from backend.scraper.jumia import extract_jumia_results

def test_extract_jumia_results_success():
    # Construct path to the sample HTML file
    sample_path = os.path.join(os.path.dirname(__file__), "../../samples/jumia_sample.html")
    
    with open(sample_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    results = extract_jumia_results(html_content)

    # Basic assertions
    assert len(results) == 2
    
    # Check first item (iPhone)
    iphone = results[0]
    assert iphone["title"] == "Apple iPhone 13 - 128GB - Midnight"
    assert iphone["price"] == 8500.0
    assert iphone["currency"] == "MAD"
    assert "iphone-13-128gb-black-654321.html" in iphone["url"]
    assert iphone["platform"] == "jumia"
    assert iphone["rating"] == 4.5

    # Check second item (Samsung)
    samsung = results[1]
    assert samsung["title"] == "Samsung Galaxy S21 - 128GB - Gray"
    assert samsung["price"] == 6200.0
    assert samsung["rating"] == 4.0

def test_extract_jumia_results_empty():
    html_content = "<html><body><div class='no-products'></div></body></html>"
    results = extract_jumia_results(html_content)
    assert len(results) == 0

def test_extract_jumia_results_invalid_price():
    html_content = """
    <div class="c-product-item">
        <h3 class="name">Broken Product</h3>
        <div class="prc">Price on request</div>
        <a class="core" href="/broken.html"></a>
    </div>
    """
    results = extract_jumia_results(html_content)
    # The scraper should skip items where price is None
    assert len(results) == 0
