from models import ABCModel

import os
import requests
import time

class APIModel(ABCModel):
    def __init__(self, default_params_path:str = 'models/default_params_api.json', **kwargs):
        super().__init__(default_params_path, **kwargs)

    def load(self, **kwargs):
        if 'HF_TOKEN' not in os.environ:
            print('[ERROR] HF_TOKEN not found in the environment.')

        auth = "Bearer " + os.environ.get('HF_TOKEN')

        self.headers = {"Authorization": auth}

        model_name = kwargs.get("model_name", "microsoft/phi-3.5-mini-instruct")

        self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"

    def prompt(self, query: str, params:dict=None, **kwargs) -> str:
        
        params = self._merge_and_set_params(params)

        data = {
            "inputs": query,
            "parameters": params
        }

        for _ in range(4):
            response = requests.post(self.api_url, headers=self.headers, json=data)
            try:
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
        
        return "[ERROR] Error generating a response!"