from models import ABCModel

import torch
from transformers import  BitsAndBytesConfig
from transformers import LlamaTokenizer, LlamaForCausalLM
        
DEFAULT_MODEL = "openlm-research/open_llama_7b_v2"

class LocalDecoderModel(ABCModel):

    def __init__(self, default_params_path:str = 'models/default_params_local.json', **kwargs):
        super().__init__(default_params_path, **kwargs)

    def load(self, **kwargs):
        model = kwargs.get("model", None)

        if not model:
            tokenizer = LlamaTokenizer.from_pretrained(DEFAULT_MODEL)

            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True,  # Use 8-bit quantization
            )
            
            model = LlamaForCausalLM.from_pretrained(
                DEFAULT_MODEL,
                device_map='auto',
                pad_token_id=tokenizer.eos_token_id,
                quantization_config=quantization_config,
            )
        
        # If model is provided, tokenizer must be provided as well
        else:
            tokenizer = kwargs.get("tokenizer", None)
            if not tokenizer:
                print("[ERROR] tokenizer is None but model is provided. Make sure to provide the model tokenizer as an argument.")
                return

        model = model.eval() # Set the model to evaluation mode

        device = model.device

        display_memory = kwargs.get("display_memory", False)

        if display_memory: # Display device memory
            allocated_memory = torch.cuda.memory_allocated(device)
            reserved_memory = torch.cuda.memory_reserved(device)
            max_memory = torch.cuda.get_device_properties(device).total_memory

            print(f"Allocated: {allocated_memory / (1024**2):.2f} MB")
            print(f"Reserved:  {reserved_memory / (1024**2):.2f} MB")
            print(f"Total:     {max_memory / (1024**2):.2f} MB")
            print(model.device)

        self.tokenizer = tokenizer
        self.model = model
        self.device = device

        print("Local model successfuly loaded!")


    def prompt(self, query: str, params:dict=None, **kwargs) -> str:

        chat_like = kwargs.get('chat_like', False)

        params = self._merge_and_set_params(params)

        if chat_like:
            return self._prompt_chat(query, params)
        else:
            return self. _prompt_completion(query, params)
    

    def _prompt_chat(self, query:str, params:dict) -> str:
        # TODO implement chat-like
        return ""

    def _prompt_completion(self, query:str, params:dict) -> str:
        
        input_ids = self.tokenizer.encode(query, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                input_ids,
                **params
            )
   
        generated_tokens = outputs[:, input_ids.size(1):]  # Exclude input tokens

        # Decode new tokens
        out = self.tokenizer.decode(generated_tokens[0], skip_special_tokens=True)

        with torch.no_grad():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()

        return out