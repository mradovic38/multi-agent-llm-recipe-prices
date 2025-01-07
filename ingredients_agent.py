import json
from typing import List

class IngredientsAgent():
    def __init__(self, model, prompt_path='ingredients_prompt.txt', ingredients_tag="<ingredients>", exclusions_tag = "<exclude>"):
        self.model = model

        self.prompt = open(prompt_path).read()
        self.ingredients_tag = ingredients_tag
        self.exclusions_tag = exclusions_tag
        
    def extract_ingredients(ingredients, exclude: List[str]):
        print("Extracting ingredients...")
        
        exclude = ', '.join(srt(x) for x in exclude)
        response = self._query_llm(ingredients, )
        ingredients_structured = json.loads(response)

        return 

    
    def _convert_units(self, ingredients):
        for ingredient in ingredients:
            ingredient['unit'] = lower(ingredient['unit']).replace(' ', '')
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
                

    def _query_llm(self, ingredients, exclude):
        query = self.prompt.replace(self.ingredients_tag, ingredients)
        query = query.replace(self.exclusions_tag, exclude)

        generated_text = self.model.prompt(query)

        code_match = re.search(r"(.*?)```", text_after_query, re.DOTALL)
        if code_match:
            generated_code = code_match.group(1).strip()
        else:
            generated_code = ''

  