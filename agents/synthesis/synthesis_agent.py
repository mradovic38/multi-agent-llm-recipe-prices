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


    def synthesize(self, user_input, data):

        print('Synthesizing the answer...')
        recipes_data, bill_data, total_price = data 
        
        response = self._query_llm(user_input, recipes_data, bill_data, total_price)

        return response
        

    def _query_llm(self, user_input:str, recipes_data, bill_data, total_price):
        
        data_input = ''
        if recipes_data:
            data_input += f'\n**Recipes:**\n```json\n{recipes_data}\n```'
        if bill_data:
            data_input += f'\n**Products:**\n```json\n{recipes_data}\n```\n'
        if total_price:
            data_input += f'\n**Total price:**\n{total_price}\n'


        query = self.prompt_text.replace(self.user_input_tag, user_input)
        query = query.replace(self.data_tag, data_input)
        
        generated_text = self.model.prompt(query)
        text_after_query = generated_text.split(query, 1)[-1]
        
        response = re.search(r"(.*?)<end>", text_after_query, re.DOTALL)

        if response:
            response = response.group(1).strip()
        else:
            return "Response could not be generated."


        return response