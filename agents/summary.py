from agents.ABCAgent import ABCAgent

class SummaryAgent(ABCAgent):
    def prompt(self, input, parameters=None) -> str:
        return self.model.prompt("summarize: " + input, parameters)