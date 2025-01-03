from product import Product
from scraped_to_sql import ScrapedToSqlConverter

from abc import ABC, abstractmethod
from typing import List

class Scraper(ABC):
    def __init__(self, base_url: str, db_url: str = "sqlite:///products.db") -> None:
        self.base_url = base_url
        self.converter = ScrapedToSqlConverter(db_url)

    def search_and_convert(self, search_terms: List[str]) -> None:
        for st in search_terms:
            results = self.search_single(st)
            self.converter.bulk_insert_from_products(results)

            all_products = self.converter.get_all_products()
            for product in all_products:
                print(product)

    @abstractmethod
    def search_single(self, search_term: str) -> List[Product]:
        pass 