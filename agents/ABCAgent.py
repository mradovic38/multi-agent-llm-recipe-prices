class ABCAgent:
    def __init__(self, model, tools=None, examples=None):
        self.model = model
        
    def prompt(self, input: str) -> str:
        return ''