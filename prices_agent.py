from scraping.scraper import Scraper
from scraping.prices_extraction import PriceExtractor
from scraping.database_manager import DatabaseManager
from ingredient import Ingredient

from typing import List

class PricesAgent():
    def __init__(self, scraper: Scraper, extractor: PriceExtractor, manager:DatabaseManager, prompt_path='prices_prompt.txt', 
                 ingredients_tag='<ingredients>', conditions_tag='<condition>') -> None:
        self.scraper = scraper
        self.extractor = extractor
        self.manager = manager
        self.prompt = open(prompt_path).read()
        self.ingredients_tag = ingredients_tag
        self.conditions_tag = conditions_tag 


    def get_prices(self, ingredients: List[Ingredient], condition: str):
        ingredients = {ingredient.name: {'amount': ingredient.amount, 'unit': ingredient.unit} for ingredient in ingredients} 
        

        print("Searching the web...")
        self.scraper.search_and_convert(ingredients.keys())

        print("Filtering products...")
        self.extractor.fill_helper_table(ingredients)

        self._query_llm(''.join(ingredients.keys()), condition)

        

    def _query_llm(self, ingredients:str, condition:str):
        self.prompt.replace(self.ingredients_tag, ingredients)
        self.prompt.replace(self.conditions_tag, condition)

        



if __name__ == '__main__':
    from scraping.prices_scraper import PriceScaper
    ps = PriceScaper()
    extractor = PriceExtractor()
    manager = DatabaseManager()
    pa = PricesAgent(scraper=ps, extractor=extractor, manager=manager)

    ingredients = [
        Ingredient('chicken', 700, 'g')
    ]

    pa.get_prices(ingredients)
    



    
"""
SELECT *
FROM products
________________
WHERE product_name IN ('flour', 'water', 'dry yeast', 'salt')
  AND price < 100
GROUP BY product_name, price
HAVING SUM(price) > 1000;
"""