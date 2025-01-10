import torch
import time
import re
import requests
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

# Zbog siromastva i manjka vremena promptujemo online modele nekad
# Mozda oba decoder i encoder decoder treba da imaju prompt ABCModel koji ima prompt str, dict -> str

class ABCDecoderModel:
    def prompt(self, input_t, parameters) -> str:
        return ''
        

class APIDecoderModel(ABCDecoderModel):
    def prompt(self, input_t, parameters=None) -> str:
        if parameters is None:
            parameters = {
                "max_new_tokens": 200,
                "min_length": 10,
                "temperature": 0.6,
                "top_p": 0.9,
                "num_beams": 3,
                "length_penalty": 0.4,
                "do_sample": True,
                "use_cache": True,
                "early_stopping": True,
            }

        API_URL = "https://api-inference.huggingface.co/models/microsoft/phi-3.5-mini-instruct"
        auth = 'Bearer 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'
        headers = {"Authorization": auth}

        data = {
            "inputs": input,
            "parameters": parameters # {
                # "max_new_tokens": 20,
                # "min_length": 10,
                # "temperature": 0.6,
                # "top_p": 0.9,
                # "num_beams": 3,
                # "length_penalty": 0.4,
                # "do_sample": True,
                # "use_cache": True,
                # "early_stopping": True
            #}
        }

        for _ in range(4):
            response = requests.post(API_URL, headers=headers, json=data)
            try:
                # print(response.json()[0])
                return response.json()[0]['generated_text']
            except:
                print(response)
                try:
                    print(response.json())
                except:
                    pass
                time.sleep(3)
        if response.status_code == 200:
            print(response.json())
        else:
            print('response code != 200')
            print(response.status_code)
        return "<ERROR>"

from transformers import LlamaTokenizer, LlamaForCausalLM

class LocalDecoderModel(ABCDecoderModel):
    def __init__(self):
        #model_name = "phi-3.5-mini-instruct"
        #model_name = "phi-3.5-mini-instruct"
        model_name = "openlm-research/open_llama_7b_v2"#"/teamspace/studios/this_studio/multi-agent-llm-recipe-prices/models/zephyr-7b-beta-local"
        # tokenizer = AutoTokenizer.from_pretrained(model_name)
        # device = "cpu"
        tokenizer = LlamaTokenizer.from_pretrained(model_name)
        quantization_config = BitsAndBytesConfig(
            load_in_8bit=True,  # Use 8-bit quantization
        )
        model = LlamaForCausalLM.from_pretrained(
            model_name,
            device_map='auto',
            pad_token_id=tokenizer.eos_token_id,
            quantization_config=quantization_config,
        ).eval()
 
        device = model.device

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

    def move_to_cpu(self):
        self.model.to('cpu')

    def move_to_gpu(self):
        self.model.to(self.device)
    
    def assistant_only(self, model_output):
        assistant_content = re.search(r"<\|assistant\|>(.*?)(?=<|$)", model_output, re.DOTALL)
        if assistant_content:
            assistant_response = assistant_content.group(1).strip()
            return assistant_response
        return ""

    DEFAULT_GENERATION_PARAMETERS = {
        "max_new_tokens": 512,
        "do_sample": True,
        "temperature": 0.6,
        "top_p": 0.95,
        "pad_token_id": None,
        "eos_token_id": None,
        "num_return_sequences": 1,
        "early_stopping": True,
    }

    def prompt(self, input_t, parameters=None) -> str:
        final_parameters = {**self.DEFAULT_GENERATION_PARAMETERS, **(parameters or {})}
        final_parameters["pad_token_id"] = self.tokenizer.pad_token_id
        final_parameters["eos_token_id"] = self.tokenizer.eos_token_id

            # parameters = {
            #     "max_new_tokens": 1000,
            #     "min_length": 10,
            #     "temperature": 0.6,
            #     "top_p": 0.9,
            #     "num_beams": 4,
            #     "length_penalty": 0.4,
            #     "do_sample": True,
            #     "use_cache": True,
            #     "early_stopping": True
            # }

        # inputs_t = self.tokenizer(input, return_tensors="pt", truncation=True).to(self.model.device)
        #inputs_t = self.tokenizer.apply_chat_template(input, tokenize=True, add_generation_prompt=True, return_tensors="pt").to(self.model.device)
        input_ids = self.tokenizer.encode(input_t, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids,
                **final_parameters
            )
   
        generated_tokens = outputs[:, input_ids.size(1):]  # Exclude input tokens

        # Decode the new tokens
        out = self.tokenizer.decode(generated_tokens[0], skip_special_tokens=True)
        #input.to('cpu')
        #del input
        with torch.no_grad():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
       # if only_assist:
           # return self.assistant_only(out)

        return out

    def free(self):
        try:
            del self.model
        except:
            pass

        try:
            del self.tokenizer
        except:
            pass
        torch.cuda.empty_cache()
        torch.cuda.synchronize()


if __name__ == "__main__":
    lmodel = LocalDecoderModel()
    resp = lmodel.prompt([
        {
            "role": "system",
            "content": open('multi-agent-llm-recipe-prices/agents/synthesis/prompts/system_prompt.txt').read()
        },
        {
            "role": "user",
            "content": open('multi-agent-llm-recipe-prices/agents/synthesis/prompts/user_prompt.txt').read()
        }
    ])
    lmodel.free()
    print(resp)