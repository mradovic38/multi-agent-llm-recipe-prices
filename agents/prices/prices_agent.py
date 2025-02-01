from tools.scraping.scraper import Scraper
from tools.scraping.prices_extraction import PriceExtractor
from tools.scraping.database_manager import DatabaseManager
from tools.scraping.bill_item import BillItem
from tools.ingredients.ingredient import Ingredient
from agents.ABCAgent import ABCAgent

import re
from typing import List, Tuple, Dict
from itertools import groupby

from decimal import Decimal

class PricesAgent(ABCAgent):
    def __init__(self, model, 
                 scraper: Scraper, 
                 extractor: PriceExtractor, 
                 manager:DatabaseManager, 
                 prompt_path='agents/prices/prompts/prices_prompt.txt', 
                 params_path = 'agents/prices/params.json',
                 ingredients_tag='<ingredients>', 
                 conditions_tag='<conditions>') -> None:
        
        super().__init__(model, prompt_path, params_path)

        self.scraper = scraper
        self.extractor = extractor
        self.manager = manager

        self.ingredients_tag = ingredients_tag
        self.conditions_tag = conditions_tag 

    def _get_top_articles_and_total_price(self, items:List[BillItem]) -> Tuple[Dict[str, BillItem], float]:
        """
        Gets the top articles for each SQL query response.

        Args:
            items (List[BillItem]): A list of bill items sorted by relevancy

        Returns:
            Dict[str, BillItem]: Dictionary of the top BillItems for each search term.
            float: Total price - a sum of all the top ranked products.
        """

        items.sort(key=lambda x: x.search_term)
        grouped_items = groupby(items, key=lambda x: x.search_term)
        top_articles = {}

        for search_term, items_iter in grouped_items:
            # Get the first item from each group
            top_articles[search_term] = list(items_iter)[0]
        
        total_price = 0

        for search_term, top_item in top_articles.items():
            total_price += top_item.price_for_amount

        return top_articles, total_price

    def get_prices(self, ingredients, conditions: List[str] = []) -> Tuple[Dict[str, BillItem], float]:
        """
        Gathers prices of all of the given ingredients, with respect to provided conditions.

        Args:
            ingredients: A list of ingretients or a list of strings depicting ingredients.
            conditions (List[str]): A list of conditions. Defaults to an empty list.

        Returns:
            Dict[str, BillItem]: Dictionary of the top BillItems for each search term.
            float: Total price - a sum of all the top ranked products.
        """

        # If no ingredients provided
        if len(ingredients) == 0:
            return {}, Decimal(0)

        # If ingredients is a list of strings
        if not isinstance(ingredients[0], Ingredient):
            ingredients_new = []
            for i in ingredients:
                ingredients_new.append(Ingredient(i, 0, "any"))
            ingredients=ingredients_new

        # Convert to dictionary   
        ingredients_dict = {ingredient.name: {'amount': ingredient.amount, 'unit': ingredient.unit} for ingredient in ingredients} 
        
        conditions_text = ", ".join(c for c in conditions)
        

        print("Searching the web...") # Explain the current step to the user
        # Searches for the keywords on a grocery store website and stores the data in a cache SQL database 
        self.scraper.search_and_convert(list(ingredients_dict.keys()))
        

        print("Filtering products...") # Explain the current step to the user
        # Filters the cache database with the reqiered ingredients to later query the SQL database.
        self.extractor.fill_helper_table(ingredients_dict)

        # Query the LLM to generate the SQL query
        sql_query = self._query_llm(ingredients=', '.join(ingredients_dict.keys()), conditions=conditions_text)

        # Display the generated SQL code.
        print("-"*100)
        print("[PRICES] Generated SQL:")
        print(sql_query)
        print("-"*100)
        result = self.extractor.execute_queries([sql_query])

        # Gather top products and calculate total price
        x = self._get_top_articles_and_total_price(result)

        # Display gathered items
        print("-"*100)
        print("[PRICES] Gathered products:")
        print(x)
        print("-"*100)

        return x

        

    def _cleanup_response(self, generated_text) -> str: 
        code_match = re.search(r"(.*?)```", generated_text, re.DOTALL)
        
        if code_match:
            generated_code = code_match.group(1).strip()
        else:
            generated_code = ""

        return "SELECT * FROM product_helper " + generated_code


    def _build_query(self, **kwargs) -> str:
        ingredients = kwargs['ingredients']
        condition = kwargs.get('conditions', '')

        query = self.prompt_text.replace(self.ingredients_tag, ingredients)
        query = query.replace(self.conditions_tag, condition)