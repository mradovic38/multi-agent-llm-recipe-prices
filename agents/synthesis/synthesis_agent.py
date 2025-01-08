from recipes_rag import RecipesRAG

import re
import json
from dataclasses import asdict


class SynthesisAgent():

    def __init__(self, model, prompt_path:str='multi-agent-llm-recipe-prices/agents/synthesis/prompts/synthesis_prompt.txt', 
    user_input_tag:str = '<user-input>', data_tag:str = '<data>'):

        with open(prompt_path, 'r') as file:
            self.prompt_text = file.read()

        self.user_input_tag = user_input_tag
        self.data_tag = data_tag

        self.model = model

    def total_price(self, bill_data, items_ids):
        return 0 # TODO

    def synthesize(self, user_input, data):

        print('Synthesizing response...')
        recipes_data = data.get('recipes', '')
        if recipes_data:
            recipes_data = json.dumps(recipes_data, indent=2)
        bill_data = data.get('bill', '')
        if bill_data:
            bill_data = json.dumps([asdict(item) for item in bill_data], indent=2)
        
        
        response = self._query_llm(user_input, recipes_data, bill_data)

        return response
        

    def _query_llm(self, user_input:str, recipes_data:str='', bill_data:str=''):
        
        data_input = ''
        if recipes_data:
            data_input += f'\n**Recipes:**\n```json\n{recipes_data}\n```'
        if bill_data:
            data_input += f'\n**Products:**\n```json\n{recipes_data}\n```\n'


        query = self.prompt_text.replace(self.user_input_tag, user_input)
        query = query.replace(self.data_tag, data_input)
        
        generated_text = self.model.prompt(query)
        text_after_query = generated_text.split(query, 1)[-1]
        
        print(text_after_query)
        print('-'*100)
        response = re.search(r"(.*?)<end>", text_after_query, re.DOTALL)

        if response:
            response = response.group(1).strip()
        else:
            return "Response could not be generated."


        return response