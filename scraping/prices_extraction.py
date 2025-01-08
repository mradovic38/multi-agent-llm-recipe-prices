from database_manager import DatabaseManager
from sql_tables import ProductSQL, ProductHelper
from bill_item import BillItem

from sqlalchemy import text, select, or_
from typing import List
import math
from decimal import Decimal

class PriceExtractor():
    def __init__(self, db_url="sqlite:///products.db"):
        self.db_manager = DatabaseManager(db_url)

        
        
    def execute_queries(self, queries):
        """
        Executes a chain of queries where each query works on the result of the previous one
        and returns a list of BillItem objects.

        :param queries: List of SQL query strings to execute in order
        :return: List of BillItem objects after all queries are executed
        """
        
        result = None
        bill_items = []

        with self.db_manager.session_scope() as session:
            
            for query in queries:
                # If it's the first query, execute directly on the database
                if result is None:
                    result = session.execute(text(query))
                else:
                    # For subsequent queries, bind the previous result
                    result = session.execute(text(query), {'previous_result': result})
                
                # Fetch all results from the query
                rows = result.fetchall()
                
                # Convert each row to a BillItem instance
                for row in rows:
                    # Extract columns from the result tuple
                    bill_item = BillItem(
                        search_term=row.search_term,
                        product_name=row.product_name,
                        url=row.url,
                        price=Decimal(row.price),
                        unit=row.unit,
                        package_size=row.package_size,
                        promo=row.promo if row.promo else 0,
                        contains_allergens=row.contains_allergens.split(",") if row.contains_allergens else [],
                        does_not_contain_allergens=row.does_not_contain_allergens.split(",") if row.does_not_contain_allergens else [],
                        amount=row.amount,
                        price_for_amount=Decimal(row.price_for_amount)
                    )
                    bill_items.append(bill_item)
            
        return bill_items
    

    def fill_helper_table(self, ingredients):
        self.db_manager.reinitialize_product_helper()

        
        with self.db_manager.session_scope() as session:
            # Filter products based on the search_terms column

            query = select(ProductSQL).filter(
                or_(
                    *[
                        # For each ingredient, we create a condition that matches both the search term and its unit
                        (ProductSQL.search_term == ingredient_name) & (ProductSQL.unit == ingredient_data['unit'])
                        for ingredient_name, ingredient_data in ingredients.items()
                    ]
                )
            )

            products = session.execute(query).scalars().all()

            # Insert the selected products into the helper table with additional price_for_amount calculation
            for product in products:
                amount = math.ceil(ingredients[product.search_term]['amount'] / product.package_size)
                price_for_amount = amount * product.price
                
                # Insert into the helper table
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

            # Commit the changes to the database
            session.commit()

if __name__=='__main__':
    pe = PriceExtractor()
    rows = pe.execute_queries(['SELECT * FROM product_helper'])
    print(rows)
