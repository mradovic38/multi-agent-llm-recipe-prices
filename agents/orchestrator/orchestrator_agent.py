from recipes_rag import RecipesRAG

import re
import torch
from agents.ABCAgent import ABCAgent

class OrchestratorAgent(ABCAgent):
# ako se buni za nasledjianje samo obrisi nasledjivanje
    def __init__(self, model, recipes_rag: RecipesRAG, ingredients_agent, prices_agent, synthesis_agent, memory_agent=None, 
    prompt_path:str='/teamspace/studios/this_studio/multi-agent-llm-recipe-prices/agents/orchestrator/prompts/orchestrator_prompt.txt', user_input_tag:str = '<user-input>'):

        self.memory_agent = memory_agent
        self.synthesis_agent = synthesis_agent
        self.ingredients_agent = ingredients_agent
        self.prices_agent = prices_agent

        self.recipes_rag = recipes_rag

        self.prompt_txt = open(prompt_path).read()
        self.user_input_tag = user_input_tag

        self.model = model

    def run_python_code(self):
        raise Exception('die')

    def dynamic_method(self):
        #recipe = self.recipes_rag.retrieve("pizza")
        #ingredients = self.ingredients_agent.extract_ingredients(recipe['ingredients'])
        #prices, total_price = self.prices_agent.get_prices(ingredients)
        #return recipe, prices, total_price
        pass
    
    def prompt(self, input):
        memory = ''
        if self.memory_agent:
            memory = self.memory_agent.get_memory()
        
        try:
            print("Planning...") # Print to let the user know which step is the current

            code = self._query_llm(input, memory)
            print(code)

            code = code = code.replace('extract_ingredients', 'self.ingredients_agent.extract_ingredients')
            code = code.replace('get_prices', 'self.prices_agent.get_prices')
            code = code.replace('query_recipes', 'self.recipes_rag.retrieve')

            code = ('\n' + code).replace('\n', '\n    ')
            runner = f"def dynamic_method(self):\n{code}"
            print('--------------------------------------------------')
            print(runner)
            print('---------------------------------------------------')

            local_scope = {}
            exec(runner, globals(), local_scope)

            # Bind the dynamically created method to the instance
            self.dynamic_method = local_scope['dynamic_method'].__get__(self)

            # Call the dynamically created method
            result = self.dynamic_method()
            # result = run_python_code()

            if result == [] or not result:
                return "Error generating response: No matching results found."

            print(result)

            response = self.synthesis_agent.synthesize(input, result)
            
            if self.memory_agent:
                self.memory_agent.memorize(input, response)

        except Exception as e:
            return f"Error generating response: Exception:\n{e}"
        

    def _query_llm(self, query:str, history:str = ''):
        a = [
            {
            "role": "system",
            "content": f"History: {history}"
        },
            {
            "role": "system",
            "content": self.prompt_txt
        },{
            "role": "user",
            "content": query
        }]
        generated_text = self.model.prompt(a)
        print(generated_text)

        pattern = r"```(?:\w+)?\n([\s\S]+?)\n```"
        matches = re.findall(pattern, generated_text, re.DOTALL)
        if len(matches) > 0:
            return matches[0]
        else:
            return 'return []'
        