import scrapy

class ProductItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    url = scrapy.Field()
    platform = scrapy.Field()
    rating = scrapy.Field()
