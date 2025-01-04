
import os
import re
import json

from typing import Dict

def parse_recipe_markdown(markdown_text: str) -> Dict:
    """
    Parse a recipe Markdown format into a structured dictionary.

    Args:
        markdown_text (str): The recipe text in Markdown format.

    Returns:
        Dict: A dictionary containing the structured recipe data.
    """
    # Initialize the result dictionary
    result = {}

    # Remove images (lines starting with "!" or containing Markdown image syntax)
    markdown_text = re.sub(r"!\[.*?\]\(.*?\)", "", markdown_text)

    # Extract metadata from the frontmatter
    frontmatter_pattern = r"---\n(.*?)\n---"
    frontmatter_match = re.search(frontmatter_pattern, markdown_text, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1).strip()
        for line in frontmatter.split("\n"):
            if ": " in line:
                key, value = line.split(": ", 1)
                result[key.strip()] = value.strip().strip("'").strip('"')

    # Extract the introduction (everything before "## Ingredients")
    intro_pattern = r"---.*?---\n(.*?)(?=\n## Ingredients)"
    intro_match = re.search(intro_pattern, markdown_text, re.DOTALL)
    if intro_match:
        introduction = intro_match.group(1).strip()
        # Remove emojis using a regex for Unicode emoji ranges
        introduction = re.sub(r"[^\w\s,.!?]", "", introduction)
        result["description"] = introduction

    # Extract ingredients (under the "## Ingredients" headline)
    ingredients_pattern = r"## Ingredients\n\n(.*?)(?=\n## Directions|\n##|$)"
    ingredients_match = re.search(ingredients_pattern, markdown_text, re.DOTALL)
    if ingredients_match:
        ingredients = [
            ingredient.strip()
            for ingredient in ingredients_match.group(1).strip().split("\n")
            if ingredient.strip()
        ]
        result["ingredients"] = ingredients

    # Extract directions (under the "## Directions" headline)
    directions_pattern = r"## Directions\n\n(.*?)(?=\nOriginally|\n##|$)"
    directions_match = re.search(directions_pattern, markdown_text, re.DOTALL)
    if directions_match:
        directions = [
            step.strip()
            for step in directions_match.group(1).strip().split("\n")
            if step.strip()
        ]
        result["directions"] = directions

    # Extract original source link if present
    source_pattern = r"Originally published at (.*)"
    source_match = re.search(source_pattern, markdown_text)
    if source_match:
        result["source"] = source_match.group(1).strip()

    return result



if __name__=='__main__':
    DIR = 'recipes_rag/content'
    
    recipes_texts = []
    paths = os.listdir(DIR)
    paths.remove("_index.md")

    for path in paths:

        with open(os.path.join(DIR, path), "r", encoding="utf-8") as file:
            recipe = file.read()

        recipe_text = parse_recipe_markdown(recipe)

        for key in list(recipe_text.keys()):
            value = recipe_text.get(key)
            recipe_text[key] = value

        recipe_text['output'] = {'title': recipe_text.get("title"),
                                 'tags': recipe_text.get("tags"),
                                 'description': recipe_text.get("description"),
                                 'ingredients': recipe_text.get("ingredients"),
                                 'directions': recipe_text.get('directions')}
        
        recipes_texts.append(recipe_text)

    with open ("recipes_rag/recipes.json", "w", encoding="utf8") as json_file:
        json_file.write(json.dumps(recipes_texts, ensure_ascii=False))