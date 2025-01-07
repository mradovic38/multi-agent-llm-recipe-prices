import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, T5ForConditionalGeneration
import time
import requests
import json

# Zbog siromastva i manjka vremena promptujemo online modele nekad

class ABCEncoderDecoderModel:
    def prompt(self, input, parameters) -> str:
        return ''

class APIEncoderDecoderModel(ABCEncoderDecoderModel):
    def __init__(self, model_name="google-t5/t5-large"):
        """google-t5/t5-large  or google-t5/t5-3b"""
        self.model_name = model_name

    def prompt(self, input, parameters=None) -> str:
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
                "early_stopping": True
            }
        
        auth = json.load(open('secret.json'))['hf_auth']
        headers = {"Authorization": auth}
        API_URL = f"https://api-inference.huggingface.co/models/{self.model_name}"

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
                return response.json()[0]['translation_text']
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

class LocalEncoderDecoderModel(ABCEncoderDecoderModel):
    def __init__(self, model_name="/teamspace/studios/this_studio/multi-agent-llm-recipe-prices/models/t5-3b"):
        """t5-large or t5-3b"""

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        # device = "cpu"

        print(f"Instancing local pretrained model {model_name}")
        model = T5ForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype = torch.float16
        ).to(device)  # type: ignore

        # device = torch.device("cuda:0")

        # Get allocated, reserved, and total memory on this GPU
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
        self.model.to('cpu')  # type: ignore
    
    def move_to_gpu(self):
        self.model.to(self.device)  # type: ignore

    def prompt(self, input, parameters=None) -> str:

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
                "early_stopping": True
            }
        
        inputs_t = self.tokenizer(input, return_tensors="pt", truncation=True).to(self.model.device)
        # outputs = model.generate(**inputs, max_new_tokens=500)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs_t,
                **parameters
            )

        out = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        inputs_t.to('cpu')
        del inputs_t
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
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
    lmodel = LocalEncoderDecoderModel()
    resp = lmodel.prompt("summarize: I want to go to a forrest and get lost forrest are nice. There is a forrest I can go in and get lost. Very nice forrest to lose myself in")
    lmodel.free()
    print(resp)