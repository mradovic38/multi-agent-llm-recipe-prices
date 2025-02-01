from agents.ABCAgent import ABCAgent
from tools.ingredients.ingredient import Ingredient

import json
from typing import List
import re

class IngredientsAgent(ABCAgent):
    def __init__(
        self, 
        model, 
        prompt_path="agents/ingredients/prompts/ingredients_prompt.txt",
        params_path='agents/ingredients/params.json',
        ingredients_tag="<ingredients>", 
        exclusions_tag = "<exclude>"):

        super().__init__(model, prompt_path, params_path)
        self.ingredients_tag = ingredients_tag
        self.exclusions_tag = exclusions_tag
        
    def extract_ingredients(self, recipe, exclude:List[str] = []) -> List[Ingredient]:
        """
        Extract ingredients in a structured format from ingredients text. Converts the units to metric system as well.

        Args:
            recipe: A recipe to extract ingredients from or a list of needed ingredients.
            exclude: A list of items to exclude when searching.

        Returns:
            List[Ingredient]: A list of ingredients to search for.
        """

        if isinstance(recipe, list):
            recipe = recipe[0]

        ingredients = recipe['ingredients']


        print("Extracting ingredients...") # Print to let the user know that the ingredients are being extracted
        exclude_str = ", ".join(exclude) if exclude else ""

        response = self._query_llm(ingredients=ingredients, exclusions=exclude_str)

        ingredients_structured = json.loads(response)

        ingredients_structured = self._convert_units(ingredients_structured)

        # Display extracted ingredients 
        print("-"*100)
        print("[INGREDIENTS] Extracted ingredients:")
        print(ingredients_structured)
        print("-"*100)

        
        return  [Ingredient(**item) for item in ingredients_structured]

    
    def _convert_units(self, ingredients) -> List[dict]:
        """
        Converts units from ingredients to metric system (since the prices data is from a European store).

        Args:
            ingredients (List[dict]): A list of ingredients

        Returns:
            List[dict]: Ingredients with converted units
        """
        for ingredient in ingredients:
            ingredient['unit'] = ingredient['unit'].replace(' ', '').lower()
            match ingredient['unit']:
                case 'l':
                    ingredient['amount'] = ingredient['amount'] * 1000
                    ingredient['unit'] = 'ml'
                case 'kg':
                    ingredient['amount'] = ingredient['amount'] * 1000
                    ingredient['unit'] = 'g'
                case 'item':
                    ingredient['unit'] = 'kom.'
                case 'oz':
                    ingredient['amount'] = ingredient['amount'] * 29.5735296
                    ingredient['unit'] = 'ml'
                case 'lbs':
                    ingredient['amount'] = ingredient['amount'] * 453.59237
                    ingredient['unit'] = 'g'
                case 'cupml':
                    ingredient['amount'] = ingredient['amount'] * 250
                    ingredient['unit'] = 'ml'
                case 'cupg':
                    ingredient['amount'] = ingredient['amount'] * 250
                    ingredient['unit'] = 'g'
                case 'tbspg':
                    ingredient['amount'] = ingredient['amount'] * 15
                    ingredient['unit'] = 'g'
                case 'tbspml':
                    ingredient['amount'] = ingredient['amount'] * 14.7867648 
                    ingredient['unit'] = 'ml'
                case 'tspg':
                    ingredient['amount'] = ingredient['amount'] * 5
                    ingredient['unit'] = 'g'
                case 'tspml':
                    ingredient['amount'] = ingredient['amount'] * 4.92892159 
                    ingredient['unit'] = 'ml'
                case 'pint':
                    ingredient['amount'] = ingredient['amount'] * 500 
                    ingredient['unit'] = 'ml'
                case _:
                    ingredient['unit'] = 'g'

        return ingredients
                

    def _build_query(self, **kwargs) -> str:
        ingredients = kwargs['ingredients']
        exclusions = kwargs.get('exclusions', '')

        query = self.prompt_txt.replace(self.ingredients_tag, ingredients)
        query = query.replace(self.exclusions_tag, exclusions)
        
        return query
    
    def _cleanup_response(self, generated_text) -> str:

        code_match = re.search(r"(.*?)```", generated_text, re.DOTALL)

        if code_match:
            generated_code = code_match.group(1).strip()
        else:
            generated_code = '[]'
        return generated_code