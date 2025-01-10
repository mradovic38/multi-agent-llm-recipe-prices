import re
import json


class SynthesisAgent():

    def __init__(self, model, prompt_path:str='agents/synthesis/prompts/synthesis_prompt.txt', 
    user_input_tag:str = '<user-input>', data_tag:str = '<data>', total_price_tag:str = '<total-price>'):

        with open(prompt_path, 'r') as file:
            self.prompt_text = file.read()

        self.user_input_tag = user_input_tag
        self.data_tag = data_tag
        self.total_price_tag = total_price_tag

        self.model = model

    def total_price_builder(self, total_price):
        price_parts = (str(total_price)).split('.')
        return f"The total cost is {price_parts[0]}.{price_parts[1][:2]} RSD."

    def synthesize(self, user_input, data):

        print('Synthesizing the answer...')
        recipes_data, bill_data, total_price = data 
        if total_price == 0:
            total_price = None

        if total_price:
            total_price = self.total_price_builder(total_price)
        
        response = self._query_llm(user_input, recipes_data, bill_data, total_price)

        if total_price:
            response += f'\n{total_price}'


        return response
        
    def _convert_to_json(self, products):
        return json.dumps(
            {key: str(item) for key, item in products.items()},
            indent=4
        )

    def _query_llm(self, user_input:str, recipes_data, bill_data, total_price):
        
        data_input = ''
        if recipes_data:
            data_input += f'**Recipes:**\n```json\n{json.dumps(recipes_data, indent=4)}\n```'
        if bill_data and len(bill_data) > 0:
            data_input += f'\n**Products:**\n```json{self._convert_to_json(bill_data)}\n```\n'

        
    
        query = self.prompt_text.replace(self.user_input_tag, user_input)
        query = query.replace(self.data_tag, data_input)
        
        if total_price:
            query = query.replace(self.total_price_tag, total_price)
        else:
            query = query.replace(self.total_price_tag, "")


        # print('--TEST---')
        # print(query)
        # print('--TEST---')

        parameters = {
            "max_new_tokens": 400,  # Adequate for recipe and price synthesis
            "do_sample": True,      # Encourage variability in phrasing
            "temperature": 0.6,    
            "top_p": 0.9,           # Use nucleus sampling for focused outputs
            "num_beams": 3,         # Explore alternative responses
            "early_stopping": True, # Stop when the output is complete
        }
        
        generated_text = self.model.prompt(query, parameters)
        # print(generated_text)
        
        response = re.search(r"(.*?)---", generated_text, re.DOTALL)

        if response:
            response = response.group(1).strip()
            return response
        else:
            return generated_text