from recipes_rag import RecipesRAG

import re
import torch


class OrchestratorAgent():

    def __init__(self, model, recipes_rag: RecipesRAG, ingredients_agent, prices_agent, synthesis_agent, memory_agent=None):

        self.memory_agent = memory_agent
        self.synthesis_agent = synthesis_agent
        self.ingredients_agent = ingredients_agent
        self.prices_agent = prices_agent

        self.recipes_rag = recipes_rag

        self.model = model

    def answer(self, user_input:str):
        memory = ''
        if self.memory_agent:
            memory = self.memory_agent.get_memory()

        try:
            print("Planning...") # Print to let the user know which step is the current

            code = self._query_llm(user_input, memory)

            code.replace('extract_ingredients', 'self.ingredients_agent.extract_ingredients')
            code.replace('get_prices', 'self.prices_agent.get_prices')
            code.replace('query_recipes', 'self.recipes_rag.retrieve')

            code = ('\n' + code).replace('\n', '\n    ')
            runner = f"""
            def run_python_code():
            {code}
            """
            exec(runner)

            result = run_python_code()

            if result == [] or not result:
                return "Error generating response: No matching results found."

            response = self.synthesis_agent.synthesize(user_input, result)
            
            if self.memory_agent:
                self.memory_agent.memorize(user_input, response)

        except Exception as e:
            return f"Error generating response: Exception:\n{e}"
        

    def _query_llm(self, query:str, history:str = ''):
        user_input = ''
        if history:
            user_input.append(f'History: {history}\n')
        user_input.append(query)

        prompt = """
You are an orchestrator agent in a multi-agent LLM system for answering questions about recipes and grocery store prices. Your job is to generate python code that describes when to use other agents as your tools to generate your response based on a user query and optionally chat history. Here is the explanation of each tool you can call:

- `query_recipes`
  Purpose:
  Processes a provided query to retrieve `top_k` relevant recipes.

  Args:
  query (str): The search query provided to find relevant recipes.
  top_k (int, optional): The number of top matching recipes to retrieve. Defaults to 1.

  Returns:
  List[Recipe]: The top-ranked recipe (or recipes).

- `extract_ingredients`:
  Purpose:
  Extracts ingredients from a ingredients text of a recipe and returns them in a structured format.

  Args:
  ingredients (str): Ingredients section of a recipe.
  exclude_list (List[str]): Ingredients to exclude

  Returns:
  List[Ingredient]: A list of JSON ingredients with name, unit and amount parameters.

- `get_prices`
  Purpose:
  Gets the price of each given ingredients and calculates the total cost.

  Args:
  ingredients (str): Structured JSON ingredients.
  conditions (List[str]): List of conditions for grocery store search.

  Returns:
  Dict[str, List[Product]: A dict with ingredient names as keys and different product options as values for that ingredient.
  Decimal: Total price of first options for each ingredient in the dict.

Provide python code for each user request and return the results in a structured format.

---

**Example:**
**User Input**:
Give me a recipe for under 400 RSD.

***Pyhon Code**:
```python
recipes = query_recipes("recipe", top_k=100)

for recipe in recipes:
	ingredients = extract_ingredients(recipe['ingredients'])
	price, total_price = get_prices(ingredients)

	if total_price < 400:
		return recipe, price, total_price
```

---

**Example:**
**User Input**:
How to make a Caesar salad and how much are the ingredients?

***Pyhon Code**:
```python
recipe = query_recipes("caesar salad")
ingredients = extract_ingredients(recipe['ingredients'])
prices, total_price = get_prices(ingredients)

return recipe, prices, total_price
```

---

**Example:**
**User Input**:
How much are the cheapest bananas

**Pyhon Code**:
```python
prices, total_price = get_prices(["banana"], conditions=["cheapest"])
return prices, total_price
```

---

**Example:**
**User Input**:
How to make pancakes?

**Pyhon Code**:
```python
recipe = query_recipes("pancakes")
return recipe
```

---

**Example:**
**User Input**:
Find the cheapest recipe.

**Pyhon Code**:
```python
recipes = query_recipes("recipe", top_k=100)

min_price = Decimal('infinity')
min_price_recipe = None

for recipe in recipes:
	ingredients = extract_ingredients(recipe['ingredients'])
	prices, total_price = get_prices(ingredients, conditions=["cheapest"])

	if total_price < min_price:
		min_price = total_price
		min_price_recipe = recipe

return recipe, price, total_price
```

---

**Example:**
**User Input**:
Find me 5 gluten free recipes that are between 1000 and 2000 RSD. I already have flour.

**Pyhon Code**:
```python
recipes = query_recipes("recipe", top_k=100)

n_recipes = 0
recipes = []
prices = []

for recipe in recipes:
	ingredients = extract_ingredients(recipe['ingredients'], exclude_list=['flour']
	price, total_price = get_prices(ingredients, conditions=['gluten free'])

	if price > 1000 and price < 2000:
		recipes.append(recipe)
		prices.append(price)
		total_prices.append(total_price)
		n_recipes+=1
		if n_recipes == 5:
			return recipes, prices, total_prices
```

---

**Example:**
**User Input**:
History: User's mom is allergic to soy.
Generate a shopping list for 'Spaghetti Carbonara' I want to make for my mom using the cheapest available products for each ingredient.

**Pyhon Code**:
```python
recipe = query_recipes("spaghetti carbonara", top_k=1)
ingredients = extract_ingredients(recipe['ingredients'])
prices, total_price = get_prices(ingredients, conditions=["cheapest", "no soy"])

return recipe, prices, total_price
```

---

**User Input**:
History: User is allergic to peanuts.
How to make the cheapest pizza capricossa for dinner?

**Pyhon Code**:
```python
"""
        generated_text = self.model.query(query)
        
        # Extract only the generated code part
        text_after_query = generated_text.split(query, 1)[-1]
        code_match = re.search(r"(.*?)```", text_after_query, re.DOTALL)
        if code_match:
            generated_code = code_match.group(1).strip()
        else:
            generated_code = ''

        
        return generated_code