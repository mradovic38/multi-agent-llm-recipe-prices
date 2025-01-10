from scraping.scraper import Scraper
from scraping.prices_extraction import PriceExtractor
from scraping.database_manager import DatabaseManager
from ingredient import Ingredient

import re
from typing import List
from itertools import groupby
from scraping.bill_item import BillItem
from decimal import Decimal

class PricesAgent():
    def __init__(self, model, scraper: Scraper, extractor: PriceExtractor, manager:DatabaseManager, 
    prompt_path='agents/prices/prompts/prices_prompt.txt', ingredients_tag='<ingredients>', conditions_tag='<conditions>') -> None:
        self.scraper = scraper
        self.extractor = extractor
        self.manager = manager
        self.model = model
        with open(prompt_path, 'r') as file:
            self.prompt_text = file.read()
        self.ingredients_tag = ingredients_tag
        self.conditions_tag = conditions_tag 

    def _get_top_articles_and_total_price(self, items:List[BillItem]):
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

    def get_prices(self, ingredients, conditions: List[str] = []):
        if len(ingredients) == 0:
            return {}, Decimal(0)

        if not isinstance(ingredients[0], Ingredient):
            ingredients_new = []
            for i in ingredients:
                ingredients_new.append(Ingredient(i, 0, "any"))
            ingredients=ingredients_new
            
        ingredients_dict = {ingredient.name: {'amount': ingredient.amount, 'unit': ingredient.unit} for ingredient in ingredients} 
        conditions_text = ", ".join(c for c in conditions)
        

        print("Searching the web...")
        self.scraper.search_and_convert(list(ingredients_dict.keys()))
        

        print("Filtering products...")
        self.extractor.fill_helper_table(ingredients_dict)

        

        sql_query = self._query_llm(', '.join(ingredients_dict.keys()), conditions_text)
        print("-"*100)
        print("[PRICES] Generated SQL:")
        print(sql_query)
        print("-"*100)
        result = self.extractor.execute_queries([sql_query])

        x = self._get_top_articles_and_total_price(result)

        print("-"*100)
        print("[PRICES] Gathered products:")
        print(x)
        print("-"*100)

        return x

        

    def _query_llm(self, ingredients:str, condition:str):
        query = self.prompt_text.replace(self.ingredients_tag, ingredients)
        query = query.replace(self.conditions_tag, condition)

        parameters = {
            "max_new_tokens": 150,       # Sufficient for typical SQL queries
            "do_sample": True,         
            "temperature": 0.2,          
            "top_p": 0.98,              
            "num_beams": 3,              # Explore possible structured variations
            "length_penalty": 1.0,       # Neutral length preference
            "early_stopping": True,      # Stop generation when the query is complete
        }
        
        generated_text = self.model.prompt(query, parameters)

        code_match = re.search(r"(.*?)```", generated_text, re.DOTALL)

        
        if code_match:
            generated_code = code_match.group(1).strip()
        else:
            generated_code = ""

        return "SELECT * FROM product_helper " + generated_code
