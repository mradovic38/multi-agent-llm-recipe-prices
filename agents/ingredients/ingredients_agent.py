import json
from typing import List
import re
from agents.ABCAgent import ABCAgent

from ingredient import Ingredient

class IngredientsAgent(ABCAgent):
    def __init__(
        self, 
        model, 
        prompt_path="agents/ingredients/prompts/ingredients_prompt.txt", 
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

        ingredients_structured = json.loads(response)

        ingredients_structured = self._convert_units(ingredients_structured)

        print("-"*100)
        print("[INGREDIENTS] Extracted ingredients:")
        print(ingredients_structured)
        print("-"*100)

        
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
                

    def _query_llm(self, ingredients, exclusions):
        query = self.prompt_txt.replace(self.ingredients_tag, ingredients)
        query = query.replace(self.exclusions_tag, exclusions)


        parameters = {
            "max_new_tokens": 200,       # Allow sufficient space for JSON output
            "do_sample": True,        
            "temperature": 0.6,         
            "top_p": 1.0,                # Consider all high-probability tokens
            "num_beams": 3,              # Structured output exploration
            "length_penalty": 1.0,       # Neutral length preference
            "early_stopping": True,      # Stop generation when the JSON is complete
        }

        generated_text = self.model.prompt(query, parameters)

        
        code_match = re.search(r"(.*?)```", generated_text, re.DOTALL)
        if code_match:
            generated_code = code_match.group(1).strip()
        else:
            generated_code = '[]'
        return generated_code
  