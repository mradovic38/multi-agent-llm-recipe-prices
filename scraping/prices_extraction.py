from .database_manager import DatabaseManager
from .sql_tables import ProductSQL, ProductHelper

from sqlalchemy import text, select, or_
from typing import List
import math

class PriceExtractor():
    def __init__(self, db_url="sqlite:///products.db"):
        self.db_manager = DatabaseManager(db_url)

        
        
    def execute_queries(self, queries):
        """
        Executes a chain of queries where each query works on the result of the previous one.

        :param queries: List of SQL query strings to execute in order
        :return: Final result after all queries are executed
        """
        
        result = None
        
        with self.db_manager.session_scope() as session:
            

            for query in queries:
                # If it's the first query, execute directly on the database
                if result is None:
                    result = session.execute(text(query))
                else:
                    # For subsequent queries, bind the previous result
                    result = session.execute(text(query), {'previous_result': result})
                
                result = result.fetchall()
        
        return result
    

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
    rows = pe.execute_query()
    print(rows)
