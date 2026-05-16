import scrapy
import re
from scraper.spiders.items import ProductItem

class AmazonSpider(scrapy.Spider):
    name = "amazon"
    
    def __init__(self, query=None, *args, **kwargs):
        super(AmazonSpider, self).__init__(*args, **kwargs)
        self.query = query
        self.allowed_domains = ["amazon.com"]

    def start_requests(self):
        if not self.query:
            self.logger.error("No search query provided. Use -a query='your search'")
            return
        
        # Build search URL with headers for better stealth
        url = f"https://www.amazon.com/s?k={self.query}"
        yield scrapy.Request(
            url=url, 
            callback=self.parse,
            headers={
                'Referer': 'https://www.amazon.com/',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        )

    def parse(self, response):
        # Select product results
        products = response.css('div.s-result-item[data-component-type="s-search-result"]')
        
        for product in products:
            item = ProductItem()
            
            # Title
            item['title'] = product.css('h2 a span::text').get()
            
            # Price
            price_whole = product.css('.a-price-whole::text').get()
            price_fraction = product.css('.a-price-fraction::text').get()
            
            if price_whole:
                # Clean up the whole part (remove commas)
                price_str = price_whole.replace(',', '').replace('.', '')
                if price_fraction:
                    price_str += f".{price_fraction}"
                try:
                    item['price'] = float(price_str)
                except ValueError:
                    item['price'] = None
            else:
                item['price'] = None
                
            # Currency
            currency_symbol = product.css('.a-price-symbol::text').get()
            item['currency'] = currency_symbol if currency_symbol else "$"
            
            # URL
            relative_url = product.css('h2 a::attr(href)').get()
            if relative_url:
                item['url'] = response.urljoin(relative_url)
            else:
                item['url'] = None
            
            # Platform
            item['platform'] = 'amazon'
            
            # Rating
            rating_text = product.css('span.a-icon-alt::text').get()
            if rating_text:
                match = re.search(r'([0-9.]+)', rating_text)
                item['rating'] = float(match.group(1)) if match else None
            else:
                item['rating'] = None
                
            yield item

        # Pagination
        next_page = response.css('a.s-pagination-next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
