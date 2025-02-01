from agents.ABCAgent import ABCAgent

class MemoryAgent(ABCAgent):
    def __init__(self, 
                 model, 
                 prompt_path:str = "agents/memory/prompts/memory_prompt.txt",
                 params_path:str = "agents/memory/params.json",
                 memory_init:str = "", 
                 cur_val_tag:str = "<current-val>", 
                 last_query_tag:str = "<last-query>", 
                 last_output_tag:str = "<last-output>"):


        super().__init__(model, prompt_path, params_path)

        self.memory = memory_init

        self.cur_val_tag = cur_val_tag
        self.last_query_tag = last_query_tag
        self.last_output_tag = last_output_tag

    def get_memory(self) -> str:
        """
        Get the current memory value.
        """
        return self.memory

    def _set_memory(self, new_mem_val:str) -> None:
        """
        Set the memory value to new_mem_val.
        """
        self.memory = new_mem_val

    def memorize(self, query:str, response:str) -> None:
        """
        Memorizes the most important info from a conversation with a user.

        Args:
            query (str): User provided query.
            response (str): Response to user query.
        """

        print("Memorizing info...") # Print the current step

        # Query the LLM to generate a new memory value
        new_val = self._query_llm(cur_mem=self.memory, query=query, response=response)

        # Display new memory value
        print("-"*100)
        print("[MEMORY] New memory value:")
        print(new_val)
        print("-"*100)
        
        # Update memory with the new value
        self._set_memory(new_val)

    def _build_query(self, **kwargs) -> str:
        cur_val = kwargs.get('cur_mem', '')
        last_query = kwargs['query']
        response = kwargs['response']
        
        query = self.prompt_text.replace(self.cur_val_tag, cur_val)
        query = query.replace(self.last_query_tag, last_query)
        query = query.replace(self.last_output_tag, response)

        return response