from .converter import ScrapedToSqlConverter
from .product import Product

from abc import ABC, abstractmethod
from typing import List
import logging


logger = logging.getLogger(__name__)

class Scraper(ABC):
    def __init__(self, base_url: str, db_url: str = "sqlite:///products.db") -> None:
        self.base_url = base_url
        self.converter = ScrapedToSqlConverter(db_url)
        logging.basicConfig(level=logging.INFO)

    def search_and_convert(self, search_terms: List[str], force_update: bool = False) -> None:
        """Search and store products, respecting the search history unless forced."""
        for search_term in search_terms:
            try:
                if force_update or self.converter.needs_update(search_term):
                    logger.info(f"Searching for term: {search_term}")
                    try:
                        results = self.search_single(search_term)
                    except Exception as e:
                        logger.info(f"Skipping '{search_term}. No results or error.: {e}'")
                        continue
                    self.converter.bulk_insert_from_products(results)
                    self.converter.update_search_history(search_term)
                    logger.info(f"Successfully processed {len(results)} results for '{search_term}'")
                else:
                    logger.info(f"Skipping '{search_term}' - was searched recently")

            except Exception as e:
                logger.error(f"Error processing search term '{search_term}': {str(e)}")
                continue

    @abstractmethod
    def search_single(self, search_term: str) -> List[Product]:
        """Implement in subclass to perform actual web scraping."""
        pass