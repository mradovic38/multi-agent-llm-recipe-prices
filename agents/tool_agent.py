from agents.ABCAgent import ABCAgent

import inspect
import json

def function_to_schema(func) -> dict:
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    try:
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(
            f"Failed to get signature for function {func.__name__}: {str(e)}"
        )

    parameters = {}
    for param in signature.parameters.values():
        try:
            param_type = type_map.get(param.annotation, "string")
        except KeyError as e:
            raise KeyError(
                f"Unknown type annotation {param.annotation} for parameter {param.name}: {str(e)}"
            )
        parameters[param.name] = {"type": param_type}

    required = [
        param.name
        for param in signature.parameters.values()
        if param.default == inspect._empty
    ]

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": (func.__doc__ or "").strip(),
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        },
    }


def json_serialize(txt):
    a = json.dumps(txt, indent=2)
    a = a.replace('\\n', '\n')
    a = a.replace('\\t', '\t')
    a = a.replace('\\r', '\r')
    a = a.replace('\\\\', '\\')
    a = a.replace('\\"', '"')
    a = a.replace("\\'", "'")
    return a

def segment_response(txt: str):
    depth = 0
    start = 0
    data = []

    def add_element(start, end):
        if end < start:
            return
        s = txt[start:end+1]
        if s[0] == '{':
            data.append({
                'type': 'tool',
                'data': s
            })
        else:
            data.append({
                'type': 'text',
                'data': s
            })
    
    for i, c in enumerate(txt):
        if c == '{':
            depth += 1
            if depth == 1:
                add_element(start, i-1)
                start = i
        elif c == '}':
            depth -= 1
            if depth == 0:
                add_element(start, i)
                start = i+1
    if len(txt)-1 != start:
        add_element(start, len(txt)-1)
    return data

def eval_model_call(function_call, funcs):
    try:
        # function_call = {"name": "saberi", "arguments": {"a": 5, "b": 10}}
        function_name = function_call["name"]
        func = funcs[function_name]
        arguments = function_call["arguments"]
        result = func(**arguments)
        return str(result)

    except json.JSONDecodeError:
        return "Model output is not valid JSON."

def eval_model_element(el, funcs):
    print(el)
    if el['type'] == 'text':
        return el['data']
    if el['type'] == 'tool':
        return eval_model_call(json.loads(el['data']), funcs)

def calculate_price(article_prices: list, quantities: list) -> float:
    """
        Uses the price of articles and their quantities to calculate the final price.
        All inputs are numbers.
        Example:
        apple price 200 count 2
        banana price 250 count 1
        article_prices = [200, 250]
        quantities = [2, 1]
        output: 650
    """

    assert len(article_prices) == len(quantities)
    return sum(float(a)*float(b) for a, b in zip(article_prices, quantities))

def saberi(a, b):
    "adds 2 numbers a=3, b=2 saberi(3,2) = 5"
    return a+b


class ToolAgent(ABCAgent):
    # nasledjuje ABCModel koji sad ne postoji
    # Koristi jedan ABCModel kao base model

    def __init__(self, model, funcs, examples):
        self.funcs = {func.__name__: func for func in funcs}
        self.func_schemas = {name: function_to_schema(func) for name, func in self.funcs.items()}
        self.func_examples = dict()
        for name in self.funcs:
            self.func_examples[name] = examples[name]
        
        # examples moze da budu svi examples (vise od funcs)
        self.model = model
    
    def craft_prompt(self, user_prompt):
        examples = []
        available_tools = []

        # for i, x in enumerate(func_schemas.values()):
        #     available_tools.append(f"{str(i+1)}.\n{x}\n------\n")
        # available_tools = ''.join(available_tools)


        # for i, x in enumerate(func_examples.values()):
        #     examples.append(f"{str(i+1)}.\n{x}\n------\n")
        # examples = ''.join(examples)

        available_tools = json_serialize(self.func_schemas)
        examples = json_serialize(self.func_examples)

        prompt = r"""
<context>
    You are a helpful AI that can call tools using valid JSON.

    Available tools: 
    <available_tools/>

    Your output MUST be valid JSON with two keys:
    1. "name": the name of the tool/function you want to call
    2. "arguments": a JSON object with the required parameters

    For example:
    {
    "name": "multiply",
    "arguments": {
        "a": 5,
        "b": 10
    }
    } would become 50 after processing

    Only ever use { and } when processing tool calls in this response.

    All function outputs are going to be swapped for text after post processing.
</context>

Examples:
<examples/>

<system> IMPORTANT: Do not talk about being an AI or calling the function. Respond normally but integrate your function call into the response.
IMPORTANT: Let the tool do its job. Do not compute or guess what the result of the tool is. Only put the call in the correct spot. 
</system>

<instruction> Respond to the user request in a style of a waiter. Be as concise as possible. After you call the function just pretend you have the output and move on.
</instruction>


Only answer to the following user prompt
"""
        return [
            {
                "role": "system",
                "content": prompt.replace('<examples/>', examples).replace('<available_tools/>', available_tools)
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]

    def prompt(self, input, parameters=None):
        full_prompt = self.craft_prompt(input)
        response = self.model.prompt(full_prompt, parameters)
        print('--------------------------')
        print('MODEL RESPONSE')
        print('--------------------------')
        print(response)
        parts = segment_response(response)
        evaluated_parts = [eval_model_element(part, self.funcs) for part in parts]
        response = "".join(evaluated_parts)  # type: ignore
        print('----------------------------------')
        return response


from models.decoder_model import LocalDecoderModel


if __name__ == "__main__":
    try:
        lmodel = LocalDecoderModel()

        examples =  {
            'saberi': """
            <example>
                <prompt>
                    I have 7 apples in my bag and 23 apples at home. How many apples do I have?
                </prompt>
                <response>
                    You have { "name": "saberi", "arguments": { "a": 7, "b": 23 } } apples in total. Enjoy your apples.
                </response>
            </example>""",

            'calculate_price': """
            <example>
                <prompt>
                Apple cost is 50. Banana cost is 150. Chocolate is 350. I bought 3 chocolate, 5 bananas and 12 apples. What is my price?
                Pretend you are a cashier.
                </prompt>
                <response>
                    Your bill is { "name": "calculate_price", "arguments": { "article_prices": [50, 150, 350], "quantities": [12, 5, 3] } }. Have a great rest of the day.
                </response>
            </example>"""
        }
        tool_agent = ToolAgent(lmodel, [saberi, calculate_price], examples)
        resp = tool_agent.prompt(open('/teamspace/studios/this_studio/multi-agent-llm-recipe-prices/agents/synthesis/prompts/user_prompt.txt').read())
        print('FINAL RESPONSE')
        print('----------------------------------')
        print(resp)
    except Exception as e:
        print(e)
    finally:
        lmodel.free()
