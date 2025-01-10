from recipes_rag import RecipesRAG
from agents.ingredients.ingredients_agent import IngredientsAgent
from agents.synthesis.synthesis_agent import SynthesisAgent

import re
import traceback


class OrchestratorAgent():

    def __init__(self, model, recipes_rag: RecipesRAG, ingredients_agent: IngredientsAgent, 
    prices_agent, synthesis_agent: SynthesisAgent, memory_agent=None, 
    prompt_path:str='agents/orchestrator/prompts/orchestrator_prompt.txt', user_input_tag:str = '<user-input>'):

        self.memory_agent = memory_agent
        self.synthesis_agent = synthesis_agent
        self.ingredients_agent = ingredients_agent
        self.prices_agent = prices_agent

        self.recipes_rag = recipes_rag

        with open(prompt_path, 'r') as file:
            self.prompt_text = file.read()
        self.user_input_tag = user_input_tag

        self.model = model

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

            code = code = code.replace('extract_ingredients', 'self.ingredients_agent.extract_ingredients')
            code = code.replace('get_prices', 'self.prices_agent.get_prices')
            code = code.replace('query_recipes', 'self.recipes_rag.retrieve')

            code = ('\n' + code).replace('\n', '\n    ')
            runner = f"def dynamic_method(self):\n{code}"
            print("-"*100)
            print("[ORCHESTRATOR] Generated function:")
            print(runner)
            print("-"*100)

            local_scope = {}
            exec(runner, globals(), local_scope)

            # Bind the dynamically created method to the instance
            self.dynamic_method = local_scope['dynamic_method'].__get__(self)

            # Call the dynamically created method
            result = self.dynamic_method()
            # result = run_python_code()

            if result == [] or not result:
                return "Error generating response: No matching results found."

            response = self.synthesis_agent.synthesize(input, result)
            if response==None:
                return "Error generating response: Synthesis could not be performed."

            
            if self.memory_agent:
                self.memory_agent.memorize(input, response)

            return response

        except Exception as e:
            return f"Error generating response: Exception:\n{traceback.format_exc()}"
        

    def _query_llm(self, query:str, history:str = ''):
        user_input = ''
        if history:
            user_input += f'History: {history}\n'
        user_input += query

        query = self.prompt_text.replace(self.user_input_tag, user_input)
        
        parameters = {
            "max_new_tokens": 150,       # Ensure enough room for generating code
            "do_sample": True,         
            "temperature": 0.4,        
            "top_p": 1.0,                # Focus on most likely completions
            "num_beams": 5,              # Balance between diversity and accuracy
            "length_penalty": 1.0,       # Neutral length preference
            "early_stopping": True,      # Stop generation once valid code is formed
        }

        generated_text = self.model.prompt(query, parameters)
       


        code_match = re.search(r"(.*?)```", generated_text, re.DOTALL)

        if code_match:
            generated_code = code_match.group(1).strip()
        else:
            generated_code = "return []"

        
        return generated_code