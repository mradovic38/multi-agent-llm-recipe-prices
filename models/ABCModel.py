import json
from abc import ABC, abstractmethod

class ABCModel(ABC):

    def __init__(self, default_params_path:str = None, **kwargs):

        if default_params_path:
            with open(default_params_path, 'r') as f:
                self.default_params = json.load(f) 
        else:
            self.default_params = {}

        self.load(**kwargs)

    @abstractmethod
    def load(self, **kwargs):
        pass

    @abstractmethod
    def prompt(self, query: str, params:dict=None, **kwargs) -> str:
        pass

    def _merge_and_set_params(self, params:str = {}) -> str:
        params = {**self.default_params, **(params or {})}

        if self.tokenizer:
            params["pad_token_id"] = self.tokenizer.pad_token_id
            params["eos_token_id"] = self.tokenizer.eos_token_id

        return params