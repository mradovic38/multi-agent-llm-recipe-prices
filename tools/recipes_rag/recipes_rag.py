from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Dict
import json
import os

class RecipesRAG:
    def __init__(self, raw_json_file: str = 'recipes_rag/recipes.json', 
                 processed_json_file: str = 'recipes_rag/recipes_processed.json', 
                 index_file: str = "/teamspace/studios/this_studio/multi-agent-llm-recipe-prices/recipes_rag/recipes.index"):
        """Initialize the RecipesRAG class by indexing recipes."""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Use a lightweight BERT model
        self.recipes_raw = self.load_recipes(raw_json_file)
        self.recipes_processed = self.load_recipes(processed_json_file)
        self.index_file = index_file

        if os.path.exists(index_file):
            self.index = faiss.read_index(index_file)
        else:
            self.index = self._build_index()
            faiss.write_index(self.index, index_file)

    def load_recipes(self, json_file: str) -> List[Dict]:
        """Load recipes from a JSON file."""
        with open(json_file, "r", encoding="utf-8") as file:
            return json.load(file)

    def _build_index(self) -> faiss.IndexFlatIP:
        """Build FAISS index from the recipes."""
        embeddings = []
        for recipe in self.recipes_processed:
            text = f"{recipe['title']} {recipe['ingredients']} {recipe['directions']}"
            embeddings.append(self.model.encode(text))
        embeddings = np.array(embeddings).astype("float32")

        index = faiss.IndexFlatIP(embeddings.shape[1])  # Inner product for cosine similarity
        index.add(embeddings)
        return index

    def retrieve(self, query: str, top_k: int = 1, return_scores=False):
        """Retrieve the top-k most relevant recipes for the given query."""

        query = query.lower()
        query_embedding = self.model.encode(query).astype("float32").reshape(1, -1)
        scores, indices = self.index.search(query_embedding, top_k)
        # If the score is requested, include it in the response
        if return_scores:
            recipes = [
                {"recipe": self.recipes_raw[idx], "score": scores[0][i]}
                for i, idx in enumerate(indices[0]) if idx < len(self.recipes_raw)
            ]
        else:
            # Only return the recipes, without scores
            recipes = [
                self.recipes_raw[idx]
                for _, idx in enumerate(indices[0]) if idx < len(self.recipes_raw)
            ]
        print('-'*100)
        print(f'[ORCHESTRATOR][RECIPES] Relevant recipes: {recipes}')
        print('-'*100)
        return recipes
        
if __name__ == '__main__':

    # Create RecipesRAG object
    rag = RecipesRAG()

    # Retrieve recipes
    query = "peperonni pizza"
    results = rag.retrieve(query, top_k=5, return_scores=True)
    for result in results:
        print(f"Title: {result['recipe']['title']}, Score: {result['score']}")