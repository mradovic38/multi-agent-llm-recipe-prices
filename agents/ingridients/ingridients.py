import json
from typing import List
import re
from agents.ABCAgent import ABCAgent

class IngredientsAgent(ABCAgent):
    def __init__(self, model, prompt_path="/teamspace/studios/this_studio/multi-agent-llm-recipe-prices/agents/ingridients/prompts/ingredients_prompt.txt", ingredients_tag="<ingredients>", exclusions_tag = "<exclude>"):
        super().__init__(model)
        self.model = model
        self.prompt_txt = open(prompt_path).read()
        self.ingredients_tag = ingredients_tag
        self.exclusions_tag = exclusions_tag
        
    def extract_ingredients(self, ingredients, exclude):
        print("Extracting ingredients...")
        exclude = ", ".join([str(x) for x in exclude])
        query = self.prompt_txt.replace(self.ingredients_tag, ingredients)
        query = query.replace(self.exclusions_tag, exclude)
        response = self._prompt(query)

        print(response)
        ingredients_structured = json.loads(response)
        
        return 

    
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
                

    def _prompt(self, input):
        generated_text = self.model.prompt(input)
        # generated text treba da se pretvori u json ako nije
        code_match = re.search(r"(.*?)```", generated_text, re.DOTALL)
        if code_match:
            generated_code = code_match.group(1).strip()
        else:
            generated_code = ''
        return generated_code
  