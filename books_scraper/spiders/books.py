from typing import Any

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response: Response, **kwargs: Any):
        for book_url in response.css("article.product_pod h3 a::attr(href)").getall():
            yield response.follow(book_url, self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_book(self, response):
        title = response.css("h1::text").get()
        price = response.css("p.price_color::text").re_first(r"£\d+\.\d")
        amount_in_stock = response.css("p.instock.availability::text").re_first(r"\d+")
        rating_class = response.css("p.star-rating::attr(class)").get()
        rating = self.get_rating(rating_class)
        category = response.css("ul.breadcrumb li:nth-child(3) a::text").get()
        description = response.css("#product_description ~ p::text").get()
        upc = response.css("table.table.table-striped tr:nth-child(1) td::text").get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }

    @staticmethod
    def get_rating(rating_class):
        """Map star rating class names to integers."""
        rating_mapping = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }
        if rating_class:
            rating_word = rating_class.replace("star-rating", "").strip()
            return rating_mapping.get(rating_word, None)
        return None
