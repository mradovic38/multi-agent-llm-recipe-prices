from product import Product

from abc import ABC, abstractmethod
from typing import List

class Scraper(ABC):
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    @abstractmethod
    def search(self, search_term) -> List[Product]:
        pass