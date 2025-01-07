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


    def get_prices(self, ingredients: List[Ingredient], conditions: List[str]):
        ingredients = {ingredient.name: {'amount': ingredient.amount, 'unit': ingredient.unit} for ingredient in ingredients} 
        conditions_text = ", ".join(c for c in conditions)

        print("Searching the web...")
        self.scraper.search_and_convert(ingredients.keys())

        print("Filtering products...")
        self.extractor.fill_helper_table(ingredients)

        sql_query = self._query_llm(''.join(ingredients.keys()), conditions_text)

        result = self.extractor.execute_queries([sql_query])

        return result

        

    def _query_llm(self, ingredients:str, condition:str):
        query = self.prompt.replace(self.ingredients_tag, ingredients)
        query = query.replace(self.conditions_tag, condition)
        
        generated_text = self.model.prompt(query)
        
        code_match = re.search(r"(.*?)```", text_after_query, re.DOTALL)
        if code_match:
            generated_code = code_match.group(1).strip()
        else:
            generated_code = ''

        



if __name__ == '__main__':
    from scraping.prices_scraper import PriceScaper
    ps = PriceScaper()
    extractor = PriceExtractor()
    manager = DatabaseManager()
    pa = PricesAgent(scraper=ps, extractor=extractor, manager=manager)

    ingredients = [
        Ingredient('chicken', 700, 'g')
    ]
    conditions = 'no soy'

    pa.get_prices(ingredients)