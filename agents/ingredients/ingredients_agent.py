import json
from typing import List
import re
from agents.ABCAgent import ABCAgent

from ingredient import Ingredient

class IngredientsAgent(ABCAgent):
    def __init__(
        self, 
        model, 
        prompt_path="/teamspace/studios/this_studio/multi-agent-llm-recipe-prices/agents/ingredients/prompts/ingredients_prompt.txt", 
        ingredients_tag="<ingredients>", exclusions_tag = "<exclude>"):
        super().__init__(model)
        self.model = model
        self.prompt_txt = open(prompt_path).read()
        self.ingredients_tag = ingredients_tag
        self.exclusions_tag = exclusions_tag
        
    def extract_ingredients(self, recipe, exclude:List[str] = []):
        if isinstance(recipe, list):
            recipe = recipe[0]

        ingredients = recipe['ingredients']

        print("Extracting ingredients...")
        exclude_str = ", ".join(exclude) if exclude else ""

        response = self._query_llm(ingredients, exclude_str)

        print("-"*100)
        print("[INGREDIENTS] Extracted ingredients:")
        print(response)
        print("-"*100)

        ingredients_structured = json.loads(response)
        
        return  [Ingredient(**item) for item in ingredients_structured]

    
    def _convert_units(self, ingredients):
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
                case _:
                    ingredient['unit'] = 'g'
                

    def _query_llm(self, ingredients, exclusions):
        query = self.prompt_txt.replace(self.ingredients_tag, ingredients)
        query = query.replace(self.exclusions_tag, exclusions)

        generated_text = self.model.prompt(query)
        text_after_query = generated_text.split(query, 1)[-1]
        # print(text_after_query)
        
        code_match = re.search(r"(.*?)```", text_after_query, re.DOTALL)
        if code_match:
            generated_code = code_match.group(1).strip()
        else:
            generated_code = '[]'
        return generated_code
  