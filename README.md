# Multi-Agent LLM System for Recipes and Prices

This project focuses on the development of a system of LLM agents designed to assist users with meal planning and simplify the process of purchasing necessary ingredients. The system is centered around two key domains: culinary recipes and grocery item prices. It enables users to submit queries that can span one or both domains, such as requesting a recipe with cost-effective ingredient choices based on current prices or calculating the required budget to prepare a specific dish. The agents utilize specialized tools for gathering and processing data from relevant knowledge bases. The primary goal of this system is to help users efficiently and affordably plan their daily meals in a practical and accessible way.

## Table of Contents
1. [Problem Analysis](#1-problem-analysis)
2. [Agent Descriptions](#2-agent-descriptions)
3. [System Architecture](#3-system-architecture)
4. [Conclusions](#4-conclusions)

## 1. Problem Analysis
The main goal of this project is to develop a system of LLM agents that address users' needs for easier meal planning and cost optimization during grocery shopping. Users seek the ability to search, combine, and utilize information from two key knowledge bases—recipes and grocery store prices. The system enables personalized meal creation based on available ingredients and current prices, providing precise, relevant, and coherent responses to complex queries.

Some of the problems this system aims to solve include:
- Finding recipes for a specific meal.
- Adapting recipes based on current ingredient prices, mentioned allergies, or already purchased groceries.
- Calculating the total cost of ingredients required to prepare a dish.
- Tracking current prices and promotions of grocery items in stores, facilitating decision-making during shopping.

Examples of queries the system should handle:
1. "Find a lunch recipe that costs less than 1000 RSD."
2. "Suggest a dinner recipe without gluten and nuts, as I have allergies."
3. "Suggest a dessert recipe. I already have flour, sugar, and chocolate."
4. "Find a chicken recipe where the total cost does not exceed 1500 RSD."
5. "How do I make a chocolate cake?"
6. "How much do bananas cost?"

### 1.1 Subproblem Analysis
Given the complexity of these queries, the problem was divided into the following subproblems:
1. **Problem Interpretation** – When a user submits a query, the system must recognize which component will handle which part of the task.
2. **Ingredient Formatting** – If a user wants to prepare a recipe, an agent must format the ingredients into a structure that is easy for the rest of the system to use.
3. **Price Information Retrieval** – How to efficiently find all necessary information about ingredient prices for a recipe with specific constraints?
4. **Information Synthesis** – Synthesizing all necessary information from retrieved recipe and price data.
5. **Storing Necessary Information** – After completing a query, what information needs to be remembered to ensure smooth conversation?

Based on these defined problems, the system will include five agents, each addressing one of these issues. The agents are described in the following section.


## 2. Agent Descriptions
All agents use the same 8-bit OpenLLaMA 7B model due to resource constraints. The `all-MiniLM-L6-v2` encoder is used for retrieving data from the vector database. The agents are refined using few-shot learning techniques, and the input is formatted so that the model continues generating examples, except for the memory agent, where only a role description is added to the input data.

### 2.1 Orchestrator Agent
This is the main agent responsible for generating and executing Python code, which forms the backbone of the program. Here, recipe data is retrieved from the vector database using a short query. Additionally, the price and ingredient agents are invoked in a manner similar to tools, enabling the system to potentially solve more complex relationships between recipes and their ingredient prices.

### 2.2 Ingredients Agent
The ingredient agent converts freely written ingredients into a structured JSON list. It receives text containing ingredients from the orchestrator agent and, using a unit conversion tool, converts the ingredients into metric units, returning them in JSON format with the following keys: ingredient name, unit, and quantity.

### 2.3 Prices Agent
This agent returns necessary items to the orchestrator agent, along with the total bill amount. It takes ingredients in JSON format and constraints as input. Based on this information, the agent searches the store's website, stores the results in an SQL database, and creates a query to extract price information for the ingredients. It also calculates the required quantity of each item, enabling later bill generation and the total cost of items. Since the implementation uses a Serbian grocery store data, it was necessary to translate relevant terms from English to Serbian and vice versa. The results of searched keywords are cached locally and used for the same keyword searches within the next week.

### 2.4 Synthesis Agent
After all necessary information is retrieved, a meaningful response must be returned to the user. The synthesis agent receives the execution result from the orchestrator, along with the initial query, and generates the final response based on this data.

### 2.5 Memory Agent
Based on the query and response, the memory agent stores necessary information in memory. It extracts the current memory value and, based on this value, the current query, and the response, creates a short text that connects to the user's next query, summarizing the interaction history.

## 3. System Architecture
<img src="https://github.com/user-attachments/assets/15db76d7-3844-43bb-ba4f-57d6aa2c720b" width=80%>\
*Figure 1: Diagram of the proposed solution's architecture.*

### 3.1 Example Workflow of the System
<img src="https://github.com/user-attachments/assets/f8af33ce-c73b-4f7d-bcd8-da4aae8c6135" width=100%>\
*Figure 2: Sequence diagram of an example of the system's workflow.*

1. The user submits a query:  
   *"How much does it cost to make a peanut-free chocolate cake as I have a peanut allergy?"*
2. The orchestrator searches for a recipe and generates Python code to execute:
   ```python
   recipe = query_recipes("chocolate cake")
   ingredients = extract_ingredients(recipe['ingredients'])
   prices, total_price = get_prices(ingredients, conditions=["no peanuts"])
   
   return recipe, prices, total_price
   ```
3. The recipe is retrieved from the vector database.
4. The ingredient agent extracts all ingredients from the recipe text and, using a unit conversion tool, converts them into SI units (e.g., oz. to grams) and formats them into JSON, e.g.:
   ```json
   [
     {
       "name": "bananas",
       "unit": "g",
       "amount": 400
     }
   ]
   ```
5. The ingredients and constraints are passed to the price agent, which finds the relevant items and returns them to the orchestrator.
6. The orchestrator sends the query and relevant data to the synthesis agent, which generates the response:  
   *"You will need 2040 RSD to make this cake."*
7. The memory agent summarizes key information from the input and output (e.g., that the user has a peanut allergy) and updates the memory value.

## 4. Conclusions
After implementing this system, the following conclusions were drawn:
- For better results on complex queries, a more powerful LLM for the orchestrator agent is necessary, as its task is more complex.
- Translating grocery items is not a reliable way to obtain the correct ingredients (e.g., the translation for "cream" is "krema" instead of "pavlaka").
- Fine-tuning the model or further optimizing few-shot learning prompts would likely lead to more stable results.
- Higher model temperatures help with creativity for agents generating unstructured text, while lower temperatures are better for agents requiring stricter outputs, such as code generation.
- Since LLMs are trained on a large number of Python files, they are very capable of generating stable Python code. Further testing is needed to determine whether passing Python function descriptions instead of the converted functions to JSON format is better for other tasks.
- The credibility of results largely depends on the quality of the data structure on the store's website. With higher-quality data, the system would certainly perform better.
- Smaller LLMs perform excellently for smaller tasks, but for more complex problems, larger models are a better option. The trade-off between cost/speed and output quality must be carefully examined to determine the best model.
- Due to resource constraints, this system was implemented using a single model. Results would likely improve if different models, tailored to individual agent roles, were used.

### 4.1 Performance Evaluation of the Solution
After implementing the system, the performance of each agent was assessed to identify areas for improvement:


<table>
  <thead>
    <tr>
      <th>Agent</th>
      <th>Performance Rating</th>
      <th>Proposed Improvement</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Orchestrator</td>
      <td><strong>80%</strong></td>
      <td>More powerful LLM, fine-tuning, and/or a model better suited for Python code generation</td>
    </tr>
    <tr>
      <td>Ingredients</td>
      <td><strong>60%</strong></td>
      <td>Fine-tuning, more precise measurements in the recipe database, splitting into two agents</td>
    </tr>
    <tr>
      <td>Prices</td>
      <td><strong>50%</strong></td>
      <td>More consistent item definitions on the store's website, English searches, fine-tuning, or a model better suited for SQL code generation</td>
    </tr>
    <tr>
      <td>Synthesis</td>
      <td><strong>50%</strong></td>
      <td>Fine-tuning and/or a specialized model for synthesis</td>
    </tr>
    <tr>
      <td>Memory</td>
      <td><strong>30%</strong></td>
      <td>Fine-tuning and/or a specialized model for summarization</td>
    </tr>
    <tr>
      <td colspan="3"><strong>Overall Performance Rating: 60%</strong></td>
    </tr>
  </tbody>
</table>

*Table 1: Performance evaluation of the solution.*
