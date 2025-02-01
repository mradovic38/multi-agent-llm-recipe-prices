from .database_manager import DatabaseManager
from .sql_tables import ProductSQL, ProductHelper
from .bill_item import BillItem

from sqlalchemy import text, select, or_
from typing import List
import math
from decimal import Decimal


class PriceExtractor:
    def __init__(self, db_url="sqlite:///products.db"):
        self.db_manager = DatabaseManager(db_url)

    def execute_queries(self, queries: List[str]) -> List[BillItem]:
        """
        Executes a chain of queries and returns a list of BillItem objects.

        :param queries: List of SQL query strings to execute in order.
        :return: List of BillItem objects after all queries are executed.
        """
        bill_items = []

        with self.db_manager.session_scope() as session:
            for query in queries:
                result = session.execute(text(query))
                rows = result.mappings().all()  # Fetch rows as mappings for safer access
                
                for row in rows:
                    # Safely extract values using `.get()` for fallback on missing fields
                    bill_item = BillItem(
                        search_term=row.get("search_term"),
                        product_name=row.get("product_name"),
                        url=row.get("url"),
                        price=Decimal(row.get("price", 0)),
                        unit=row.get("unit"),
                        package_size=row.get("package_size", 1),
                        promo=row.get("promo", 0),
                        contains_allergens=row.get("contains_allergens", "").split(","),
                        does_not_contain_allergens=row.get("does_not_contain_allergens", "").split(","),
                        amount=row.get("amount", 0),
                        price_for_amount=Decimal(row.get("price_for_amount", 0)),
                    )
                    bill_items.append(bill_item)

        return bill_items

    def fill_helper_table(self, ingredients: dict):
        """
        Populates the ProductHelper table with filtered products and calculates `price_for_amount`.

        :param ingredients: Dictionary of ingredient data with `amount` and `unit` keys.
        """
        self.db_manager.reinitialize_product_helper()

        with self.db_manager.session_scope() as session:
            # Build a filter query for ingredients
            conditions = [
                (ProductSQL.search_term == ingredient_name) &
                ((ProductSQL.unit == ingredient_data['unit']) | (ingredient_data['unit'] == 'any'))
                for ingredient_name, ingredient_data in ingredients.items()
            ]

            query = select(ProductSQL).filter(or_(*conditions))
            products = session.execute(query).scalars().all()

            for product in products:
                ingredient_data = ingredients[product.search_term]
                amount = math.ceil(
                    (ingredient_data.get('amount', 1) / product.package_size)
                    if ingredient_data.get('amount', 1) > 0 else 1
                )
                price_for_amount = amount * product.price

                helper_product = ProductHelper(
                    search_term=product.search_term,
                    product_name=product.product_name,
                    url=product.url,
                    price=product.price,
                    unit=product.unit,
                    package_size=product.package_size,
                    promo=product.promo,
                    contains_allergens=product.contains_allergens,
                    does_not_contain_allergens=product.does_not_contain_allergens,
                    amount=amount,
                    price_for_amount=price_for_amount
                )
                session.add(helper_product)

            session.commit()


if __name__ == '__main__':
    pe = PriceExtractor()
    rows = pe.execute_queries(['SELECT * FROM product_helper'])
    for row in rows:
        print(row)
