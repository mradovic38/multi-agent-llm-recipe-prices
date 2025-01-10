class MemoryAgent():
    def __init__(self, model, prompt_path:str="agents/memory/prompts/memory_prompt.txt",
    memory_init:str="", cur_val_tag = "<current-val>", last_query_tag="<last-query>", last_output_tag="<last-output>"):

        self.memory = memory_init

        with open(prompt_path, 'r') as file:
            self.prompt_text = file.read()

        self.cur_val_tag = cur_val_tag
        self.last_query_tag = last_query_tag
        self.last_output_tag = last_output_tag

        self.model = model

    def get_memory(self):
        return self.memory

    def _set_memory(self, new_mem_val):
        self.memory = new_mem_val

    def memorize(self, query, response):
        print("Memorizing info...")

        new_val = self._query_llm(self.memory, query, response)

        print("-"*100)
        print("[MEMORY] New memory value:")
        print(new_val)
        print("-"*100)
        
        self._set_memory(new_val)
        return

    def _query_llm(self, cur_val, last_query, response):

        query = self.prompt_text.replace(self.cur_val_tag, cur_val)
        query = query.replace(self.last_query_tag, last_query)
        query = query.replace(self.last_output_tag, response)

        parameters = {
            "max_new_tokens": 15,       # Limit to ensure concise summaries
            "do_sample": True,         
            "temperature": 0.05,         # Reduce randomness for precise summaries
            "top_p": 0.8,            
            "num_beams": 5,             # Beam search for optimal phrasing
            "length_penalty": 0.5,      # Slight preference for shorter outputs
            "early_stopping": True,     # Stop as soon as a coherent summary is generated
        }

        generated_text = self.model.prompt(query, parameters)

        
        return generated_text