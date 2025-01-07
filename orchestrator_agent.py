from recipes_rag import RecipesRAG

import re
import torch


class OrchestratorAgent():

    def __init__(self, model, recipes_rag: RecipesRAG, ingredients_agent, prices_agent, synthesis_agent, memory_agent=None, 
    prompt_path:str='orchestrator_prompt.txt', user_input_tag:str = '<user-input>'):

        self.memory_agent = memory_agent
        self.synthesis_agent = synthesis_agent
        self.ingredients_agent = ingredients_agent
        self.prices_agent = prices_agent

        self.recipes_rag = recipes_rag

        self.prompt = open(prompt_path).read()
        self.user_input_tag = user_input_tag

        self.model = model

    def answer(self, user_input:str):
        memory = ''
        if self.memory_agent:
            memory = self.memory_agent.get_memory()

        try:
            print("Planning...") # Print to let the user know which step is the current

            code = self._query_llm(user_input, memory)

            code.replace('extract_ingredients', 'self.ingredients_agent.extract_ingredients')
            code.replace('get_prices', 'self.prices_agent.get_prices')
            code.replace('query_recipes', 'self.recipes_rag.retrieve')

            code = ('\n' + code).replace('\n', '\n    ')
            runner = f"""
            def run_python_code():
            {code}
            """
            exec(runner)

            result = run_python_code()

            if result == [] or not result:
                return "Error generating response: No matching results found."

            response = self.synthesis_agent.synthesize(user_input, result)
            
            if self.memory_agent:
                self.memory_agent.memorize(user_input, response)

        except Exception as e:
            return f"Error generating response: Exception:\n{e}"
        

    def _query_llm(self, query:str, history:str = ''):
        user_input = ''
        if history:
            user_input.append(f'History: {history}\n')
        user_input.append(query)

        query = self.prompt.replace(self.user_input_tag, user_input)
        
        generated_text = self.model.prompt(query)

        code_match = re.search(r"(.*?)```", text_after_query, re.DOTALL)
        if code_match:
            generated_code = code_match.group(1).strip()
        else:
            generated_code = ''

        
        return generated_code