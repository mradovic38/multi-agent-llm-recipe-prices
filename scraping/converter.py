from typing import List
from decimal import Decimal
from datetime import datetime, timedelta
import logging
from sql_tables import ProductSQL, SearchHistory
from database_manager import DatabaseManager
from product import Product

logger = logging.getLogger(__name__)

class ScrapedToSqlConverter:
    def __init__(self, database_url: str = "sqlite:///products.db"):
        self.db_manager = DatabaseManager(database_url)

    def product_to_sql(self, product: Product) -> ProductSQL:
        """Convert a Product dataclass instance to a ProductSQL instance."""
        return ProductSQL(
            search_term=product.search_term,
            product_name=product.product_name,
            price=product.price,
            unit=product.unit,
            package_size=product.package_size,
            promo=product.promo,
            contains_allergens=",".join(product.contains_allergens) if product.contains_allergens else "",
            does_not_contain_allergens=",".join(product.does_not_contain_allergens) if product.does_not_contain_allergens else "",
            url=product.url
        )

    def bulk_insert_from_products(self, products: List[Product], batch_size: int = 1000) -> None:
        """Insert or update multiple Product dataclass instances into the database in batches."""
        with self.db_manager.session_scope() as session:
            for i in range(0, len(products), batch_size):
                batch = products[i:i + batch_size]
                for product in batch:
                    existing_product = session.query(ProductSQL).filter_by(product_name=product.product_name).first()
                    if existing_product:
                        # Update fields
                        existing_product.price = product.price
                        existing_product.promo = product.promo
                        # Add other fields as necessary
                    else:
                        # Insert new product
                        session.add(self.product_to_sql(product))
                session.commit()

    def get_all_products(self) -> List[ProductSQL]:
        """Retrieve all products from the database."""
        with self.db_manager.session_scope() as session:
            return session.query(ProductSQL).all()

    def update_search_history(self, search_term: str) -> None:
        """Update or create search history entry."""
        with self.db_manager.session_scope() as session:
            history = session.query(SearchHistory).filter_by(search_term=search_term).first()
            if history:
                history.last_searched = datetime.now()
            else:
                history = SearchHistory(search_term=search_term, last_searched=datetime.now())
                session.add(history)

    def needs_update(self, search_term: str, days: int = 7) -> bool:
        """Check if a search term needs to be updated based on last search date."""
        with self.db_manager.session_scope() as session:
            history = session.query(SearchHistory).filter_by(search_term=search_term).first()
            if not history:
                return True
            cutoff_date = datetime.now() - timedelta(days=days)
            return history.last_searched < cutoff_date