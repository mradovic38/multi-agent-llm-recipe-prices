import os
import json
import re
import string
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk
nltk.download('stopwords')

def preprocess_text(text: str) -> str:
    """Preprocess text by lowering case, removing punctuation, stopwords, and stemming."""
    
    # Convert to lowercase
    text = text.lower()

    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    text = ' '.join([word for word in text.split() if word not in stop_words])

    # Optionally, apply stemming
    stemmer = PorterStemmer()
    text = ' '.join([stemmer.stem(word) for word in text.split()])

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def preprocess_markdown_files(input_dir: str = 'recipes_rag/content', 
                              raw_output_file: str = 'recipes_rag/recipes.json',
                              processed_output_file: str = 'recipes_rag/recipes_processed.json'):
    """Preprocess recipe markdown files and save them as a JSON list."""
    recipes_raw = []
    recipes_processed = []
    image_pattern = r"!\[.*?\]\(.*?\)"  # Matches Markdown images

    for filename in os.listdir(input_dir):
        if filename.endswith(".md"):
            with open(os.path.join(input_dir, filename), "r", encoding="utf-8") as file:
                content = file.read()

            # Remove images
            content = re.sub(image_pattern, "", content)

            # Split metadata and main content
            metadata, main_content = content.split("---", maxsplit=2)[1:]
            metadata = {
                line.split(":")[0].strip(): line.split(":", maxsplit=1)[1].strip()
                for line in metadata.strip().split("\n")
                if ":" in line
            }

            # Extract sections
            sections = re.split(r"^##\s", main_content, flags=re.MULTILINE)
            sections = [s.strip() for s in sections if s.strip()]

            # Parse ingredients and directions
            ingredients, directions = None, None
            for section in sections:
                if section.startswith("Ingredients"):
                    ingredients = section.split("\n", maxsplit=1)[-1].strip()
                elif section.startswith("Directions"):
                    directions = section.split("\n", maxsplit=1)[-1].strip()
            
            recipes_raw.append({
                "title": metadata.get("title", ""),
                "tags": metadata.get("tags", "").strip("[]").replace("'", "").split(", "),
                "ingredients": ingredients if ingredients else "",
                "directions": directions if directions else "",
            })

            # Preprocess content
            preprocessed_ingredients = preprocess_text(ingredients) if ingredients else ""
            preprocessed_directions = preprocess_text(directions) if directions else ""
            preprocessed_title = preprocess_text(metadata.get("title", ""))

            recipes_processed.append({
                "title": preprocessed_title,
                "tags": metadata.get("tags", "").strip("[]").replace("'", "").split(", "),
                "ingredients": preprocessed_ingredients,
                "directions": preprocessed_directions,
            })

    # Save to JSON
    with open(raw_output_file, "w", encoding="utf-8") as json_file:
        json.dump(recipes_raw, json_file, indent=4, ensure_ascii=False)

    with open(processed_output_file, "w", encoding="utf-8") as json_file:
        json.dump(recipes_processed, json_file, indent=4, ensure_ascii=False)

# Example usage
if __name__ == '__main__':
    preprocess_markdown_files()