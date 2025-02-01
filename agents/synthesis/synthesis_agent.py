from agents.ABCAgent import ABCAgent

import re
import json


class SynthesisAgent(ABCAgent):

    def __init__(self, 
                 model, 
                 prompt_path:str = 'agents/synthesis/prompts/synthesis_prompt.txt',
                 params_path:str = 'agents/synthesis/params.json',
                 user_input_tag:str = '<user-input>', 
                 data_tag:str = '<data>', 
                 total_price_tag:str = '<total-price>'):


        super().__init__(model, prompt_path, params_path)

        self.user_input_tag = user_input_tag
        self.data_tag = data_tag
        self.total_price_tag = total_price_tag

    def total_price_builder(self, total_price):
        """
        Formats the text to display the total price to the user.
        """
        price_parts = (str(total_price)).split('.')
        return f"The total cost is {price_parts[0]}.{price_parts[1][:2]} RSD."

    def synthesize(self, user_input, data) -> str:
        """
        Synthesized the response to give the user, based on a provided data and user query.

        Args:
            user_input (str): User query to respond to.
            data: Data to be used for generating a more accurate response.

        Returns:
            str: Answer to user query.
        """

        print('Synthesizing the answer...') # Print the current step

        recipes_data, bill_data, total_price = data # Extract data from tuple

        # If total price is 0, do not display it
        if total_price == 0:
            total_price = None

        # Display total price
        if total_price:
            total_price = self.total_price_builder(total_price)
        
        # Query the LLM to synthesize data to return consistent output text.
        response = self._query_llm(query=user_input, recipes=recipes_data, bill=bill_data, price=total_price)

        if total_price:
            response += f'\n{total_price}'

        return response
        
    def _convert_to_json(self, products):
        """
        Converts to JSON to provide the LLM with more structured info.
        """
        return json.dumps(
            {key: str(item) for key, item in products.items()},
            indent=4
        )
        

    def _build_query(self, **kwargs) -> str:
        user_input = kwargs['query']
        recipes_data = kwargs.get('recipes', None)
        bill_data = kwargs.get('bill', None)
        total_price = kwargs.get('price', None)

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
            
        return query
    
    def _cleanup_response(self, generated_text) -> str:
        response = re.search(r"(.*?)---", generated_text, re.DOTALL)

        if response:
            response = response.group(1).strip()
            return response
        else:
            return generated_text